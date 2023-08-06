#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import json
import logging
import subprocess
import time
import glob

import calendar

from datetime import datetime
from datetime import timedelta
from pathlib import Path
from shutil import copy
from shutil import copytree
from tempfile import mkdtemp


KEEP_FILENAME = ".tondor_keep"


log = logging.getLogger(__name__)


def run_subprocess(args, work_dir):
    log.debug("Calling subprocess, args={:s}.".format(repr(args)))
    pr = subprocess.run(args, cwd=work_dir, check=False)
    log.info("Subprocess exited with code {:d}, args={:s}.".format(pr.returncode, repr(args)))
    pr.check_returncode()


def log_subprocess(args, work_dir, log_filepath, timeout=None):
    log.debug("Calling subprocess: {:s}, logging to {:s}.".format(repr(args), str(log_filepath)))
    with open(str(log_filepath), "at", encoding="utf-8") as logf:
        logf.write("\n{:s} Calling subprocess: {:s}.\n".format(datetime.utcnow().isoformat()[:23], repr(args)))
        logf.flush()
        pr = subprocess.run(args, cwd=work_dir, stdout=logf, stderr=logf, timeout=timeout, check=False)
        log.info("Subprocess exited with code {:d}, args={:s}.".format(pr.returncode, repr(args)))
        logf.write("\n{:s} Subprocess exited with code {:d}.\n".format(datetime.utcnow().isoformat()[:23], pr.returncode))
    pr.check_returncode()


def read_tool_def(tool_def_filepath):
    tool_def = json.loads(tool_def_filepath.read_text())
    return tool_def


def set_input_param(job_step_params, ident, value):
    for input_p in job_step_params["parameters"]:
        if input_p["ident"] == ident:
            input_p["value"] = value


def get_input_param(job_step_params, ident):
    for input_p in job_step_params["parameters"]:
        if input_p["ident"] == ident:
            return input_p["value"]
    return None


def generate_yearmonths(ym_from, ym_till):
    year = int(ym_from[:4])
    month = int(ym_from[4:6])
    yearmonths = []
    while True:
        yearmonth = "{:d}{:02}".format(year, month)
        if yearmonth > ym_till:
            break
        yearmonths.append(yearmonth)
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
    return yearmonths

def generate_timeperiod_monthly(year, month):
    year = int(year)
    month = int(month)
    startmonth = month
    endmonth = month
    enddate = calendar.monthrange(year, endmonth)[1]

    yearmonth_start = "{:d}{:02}01".format(year, startmonth)
    yearmonth_end = "{:d}{:02}{:02}".format(year, month, enddate)
    yearmonth_timeperiod = str(yearmonth_start) + '-' + str(yearmonth_end)

    return yearmonth_timeperiod

def generate_timeperiod_quaterly(year, month):
    startmonth = month
    endmonth = month + 2
    enddate = calendar.monthrange(year, endmonth)[1]

    yearmonth_start = "{:d}{:02}01".format(year, startmonth)
    yearmonth_end = "{:d}{:02}{:02}".format(year, endmonth, enddate)
    yearmonth_timeperiod = str(yearmonth_start) + '-' + str(yearmonth_end)

    return yearmonth_timeperiod


def generate_quarters(year_from, year_till):
    year = int(year_from)
    quarters = [1, 2, 3, 4]
    yearquarters = []
    while True:
        for quarter in quarters:
            yearquarter = "{:d}Q{:d}".format(year, quarter)
            yearquarters.append(yearquarter)
        if year > year_till:
            break
    return yearquarters


def month_range(yearmonth):
    year = int(yearmonth[0:4])
    month = int(yearmonth[4:6])
    start_date = datetime(year, month, 1)
    if month == 12:
        month = 1
        year += 1
    else:
        month += 1
    final_date = datetime(year, month, 1)
    return (start_date, final_date)


def quarter_range(yearquarter):
    year = int(yearquarter[0:4])
    quarter_index = int(yearquarter[5:6]) - 1
    quarter_start_months = [1, 4, 7, 10]
    start_month = quarter_start_months[quarter_index]
    start_date = datetime(year, start_month, 1)

    quarter_final_months = [3, 6, 9, 12]
    final_month = quarter_final_months[quarter_index]
    if final_month == 12:
        final_month = 1
        year += 1
    else:
        final_month += 1
    final_date = datetime(year, final_month, 1)
    return (start_date, final_date)


def archive_results(tmp_dir_tpl, src_dst_pairs):
    # Create temporary directory dedicated for this function call.
    tmp_dir = Path(mkdtemp(prefix="{:s}.".format(tmp_dir_tpl.name), suffix=".d", dir=tmp_dir_tpl.parent))

    # Create all destination directories.
    dst_dirs = [dst_path.parent for (src_path, dst_path) in src_dst_pairs]
    dst_dirs = set(dst_dirs)
    dst_dirs = sorted(dst_dirs, key=str)
    for dst_dir in dst_dirs:
        # Before any move begins, the result directory should have updated timestamp.
        # Such updated timestamp should eliminate a race condition
        # when some other process is just removing empty directories.
        # While mkdir() does not update the timestamp if the directory already exists,
        # we must update the timestamp explicitly.
        keep_filepath = dst_dir.joinpath(KEEP_FILENAME)
        try:
            keep_filepath.touch(exist_ok=True)
            keep_filepath.unlink()
        except FileNotFoundError:
            pass
        dst_dir.mkdir(parents=True, exist_ok=True)

    # Copy all source items into temporary directory.
    #
    # To ensure two items with the same name do not collide,
    # give all the items in temporary directory special suffix.
    tmp_dst_pairs = []
    for (i, (src_path, dst_path)) in enumerate(src_dst_pairs, start=1):
        tmp_path = tmp_dir.joinpath("{:s}.{:d}".format(src_path.name, i))
        if src_path.is_dir():
            copytree(str(src_path), str(tmp_path))
            log.info("Directory tree {:s} has been copied to temporary {:s}."
                     .format(str(src_path), str(tmp_path)))
        else:
            copy(str(src_path), str(tmp_path))
            log.info("File {:s} has been copied to temporary {:s}."
                     .format(str(src_path), str(tmp_path)))
        tmp_dst_pairs.append((tmp_path, dst_path))

    # Move already copied items into final destination.
    for tmp_path, dst_path in tmp_dst_pairs:
        tmp_path.rename(dst_path)
        log.info("Temporary file/dir {:s} has been moved to final {:s}."
                 .format(str(tmp_path), str(dst_path)))

    # Remove the temporary directory.
    tmp_dir.rmdir()
    log.info("Temporary directory {:s} has been removed.".format(str(tmp_dir)))


#
# Utility functions for detecting missing L2A scenes.
#

def parse_sentinel2_name(name):
    if name.endswith(".SAFE"):
        name = name[:-5]
    name_parts = name.split("_")
    info = {"name": name,
            "mission": name_parts[0][2],
            "level": name_parts[1][3:].upper(),
            "obs_date": datetime.strptime(name_parts[2], "%Y%m%dT%H%M%S"),
            "baseline": name_parts[3][1:],
            "rel_orbit": name_parts[4][1:],
            "tile": name_parts[5][1:],
            "produced_date": datetime.strptime(name_parts[6], "%Y%m%dT%H%M%S"),
            "satellite": "sentinel-2"}
    return info


def pair_sentinel2_scene_infos(scene_infos):
    # Build table of paired L1C and L2A items.
    scene_idx = {}
    for scene_info in scene_infos:
        scene_key = (scene_info["obs_date"], scene_info["tile"])
        if scene_key not in scene_idx:
            scene_idx[scene_key] = ([], [])
        if scene_info["level"] == "L1C":
            scene_idx[scene_key][0].append(scene_info)
        elif scene_info["level"] == "L2A":
            scene_idx[scene_key][1].append(scene_info)
        else:
            log.warning("Unknown level {:s} of the scene {:s}.".format(scene_info["level"], scene_info["name"]))

    # Sort the items within a pair by produced_date property.
    for (l1c, l2a) in scene_idx.values():
        l1c.sort(key=lambda info: info["produced_date"])
        l2a.sort(key=lambda info: info["produced_date"])

    return scene_idx


def filter_cloud_cover(scene_idx, max_cloud_cover):
    new_scene_idx = {}
    for (key, (l1c, l2a)) in scene_idx.items():
        item_cloud_cover = max(info["cloud_cover"] for info in [*l1c, *l2a])
        if item_cloud_cover > max_cloud_cover:
            key_date, tile = key
            log.debug("All items of the date {:s} and tile {:s} has been removed,"
                      " while the cloud cover {:f} is above {:f}."
                      .format(key_date.isoformat(), tile, item_cloud_cover, max_cloud_cover))
        else:
            new_scene_idx[key] = (l1c, l2a)
    return new_scene_idx


def compile_sentinel2level2a_glob(l1c_name):
    name_parts = l1c_name.split("_")
    mission = name_parts[0]
    obs_date = name_parts[2]
    tile = name_parts[5]
    year = obs_date[:4]
    month = obs_date[4:6]
    day = obs_date[6:8]
    name_glob = "{:s}_MSIL2A_{:s}_*_*_{:s}_*.SAFE".format(mission, obs_date, tile)
    path = Path("Sentinel2", year, month, day)
    return path, name_glob


def compile_sentinel2level2a_eodata_glob(l1c_name):
    path, name_glob = compile_sentinel2level2a_glob(l1c_name)
    path = Path(str(path).replace("Sentinel2/", "Sentinel-2/MSI/L2A/"))
    return path, name_glob


def compile_monthly_composite_filepath(archive_root, year, sitecode, month):
    countrycode = sitecode[0:2]
    yearmonth = "{:04d}{:02d}".format(int(year), month)
    startdate, enddate = month_range(yearmonth)
    # month_range returns (first day of the month, first day of the next month).
    # OPT composite naming convention uses (first day of the month, last day of the month).
    startdate = startdate.strftime("%Y%m%d")
    enddate = (enddate - timedelta(hours=12)).strftime("%Y%m%d")
    basename = "MTC_{startdate}_{enddate}_{sitecode}_OPT.tif"
    basename = basename.format(startdate=startdate, enddate=enddate, sitecode=sitecode)
    return archive_root.joinpath(str(year), countrycode, sitecode, "MTC", "OPT", basename)


def compile_quarterly_composite_filepath(archive_root, year, sitecode, quarter):
    countrycode = sitecode[0:2]
    yearquarter = "{:04d}{:02d}".format(int(year), quarter)
    log.debug(yearquarter)
    startdate, enddate = quarter_range(yearquarter)
    # month_range returns (first day of the month, first day of the next month).
    # OPT composite naming convention uses (first day of the month, last day of the month).
    startdate = startdate.strftime("%Y%m%d")
    enddate = (enddate - timedelta(hours=12)).strftime("%Y%m%d")
    basename = "MTC_{startdate}_{enddate}_{sitecode}_OPT.tif"
    basename = basename.format(startdate=startdate, enddate=enddate, sitecode=sitecode)
    return archive_root.joinpath(str(year), countrycode, sitecode, "MTC", "OPT", basename)


def find_file_in_archives(relative_path, archive_roots, error_on_missing=True):
    for archive_root in archive_roots:
        log.debug("Searching for {:s} in {:s}".format(str(relative_path), str(archive_root)))
        filepath = archive_root.joinpath(relative_path)
        if filepath.is_file():
            log.info("Found {:s} at {:s}".format(filepath.name, str(filepath)))
            return filepath
    if error_on_missing:
        # If we got up to here, then nothing is found and we must raise FileNotFoundError.
        msg = "Expected file {:s} was not found in any of the archives.".format(str(relative_path))
        log.error(msg)
        raise FileNotFoundError

def find_files_in_archives(relative_path, archive_roots, error_on_missing=True):
    filepaths = []
    for archive_root in archive_roots:
        log.debug("Searching for {:s} in {:s}".format(str(relative_path), str(archive_root)))
        path_fullpath = archive_root.joinpath(relative_path)

        filepath = glob.glob(str(path_fullpath))
        if len(filepath)>0:
           log.info("Found {} in {}".format(filepath, archive_root))
           filepaths.extend(filepath)
    log.debug("Found the following opt composite files:{}".format(filepaths))
    return filepaths


def locate_optcomposites(archive_roots, year, sitecode, training_selection, site_selection):
    # training_selection: indices of months that should be used for the training, typically 111111111111.
    # site_selection: indices of months with suitable composites for the given site, e.g.  001111111110.
    # site_selection can have four digits or 12 digits
    # Constructs expected paths to OPT composites for a given year, site and selection.
    # Months with unsuitable composite are given the value of path=None.
    log.debug("Searching for OPT composites from site={}, year={}, training_selection={}, site_selection={}"
              .format(sitecode, year, training_selection, site_selection))
    countrycode = sitecode[0:2]
    num_timesteps = len(training_selection)
    if len(site_selection) != num_timesteps:
        raise Exception("training_selection and site_selection length must have equal number of timesteps.")

    log.info("Training selection is {:s}".format(repr(training_selection)))
    log.info("Site selection is {:s}".format(repr(site_selection)))

    # Check length of the site selection depending on the year.
    if int(year) >= 2016 and num_timesteps != 12:
        raise Exception("Number of selection items for sitecode {:s} is {:d}, but it should be 12.".format(sitecode, len(site_selection)))
    if int(year) <= 2015 and num_timesteps != 4:
        raise Exception("Number of selection items for sitecode {:s} is {:d}, but it should be 12.".format(sitecode,len(site_selection)))

    optcomposite_filepaths = []
    training_timesteps = []
    site_timesteps = []

    # The site selection is a 12-character or 4-character string of ones and zeros, e.g. 011111100100.
    # The character '1' means that the month is selected.
    # The character '0' means that the month is not selected.
    for ts_index, ts_status in enumerate(training_selection):
        if int(ts_status) == 1:
            training_timesteps.append(ts_index + 1)
    log.info("training_months or quarters: {}.".format(repr(training_timesteps)))

    # Here the indexes of the timesteps from which values should be taken are used.
    for timestep_index, timestep_status in enumerate(site_selection):
        if int(timestep_status) == 1:
            site_timesteps.append(timestep_index + 1)
    log.info("site_months or quarters: {}.".format(repr(site_timesteps)))

    for timestep in training_timesteps:
        if timestep in site_timesteps:
            composite_filepath = None
            for archive_root in archive_roots:
                if num_timesteps == 12:
                    composite_filepath = compile_monthly_composite_filepath(archive_root, year, sitecode, timestep)
                else:
                    composite_filepath = compile_quarterly_composite_filepath(archive_root, year, sitecode, timestep)
                log.info("Searching for composite at {:s}.".format(str(composite_filepath)))
                if composite_filepath.is_file():
                    # If composite is found, then add it to list.
                    log.info("Found composite for site {:s}, timestep {:d} at {:s}"
                             .format(sitecode, timestep, str(composite_filepath)))
                    optcomposite_filepaths.append(composite_filepath)
                    break
            if composite_filepath is None:
                log.error("No composite was found for site {:s}, selected timestep {:d}".format(sitecode, timestep))
                raise FileNotFoundError
        else:
            # If an OPTCOMPOSITE is not in selection then it is set to NONE.
            log.info("Set optcomposite for site {:s}, timestep {:d} to None.".format(sitecode, timestep))
            optcomposite_filepaths.append(None)

    log.info("selected OPT composites for site={}, year={}, training_selection={}, site_selection={} are:"
             .format(sitecode, year, training_selection, site_selection))
    for timestep, fp in enumerate(optcomposite_filepaths):
        log.info("timestep: {:d}, composite: {:s}".format(timestep, str(fp)))
    return training_timesteps, optcomposite_filepaths


def locate_sarcomposites(archive_roots, year, sitecode):
    # Constructs expected paths to SAR composites for a given year and site.
    countrycode = sitecode[0:2]
    composite_filepaths = []
    months = [m for m in range(1, 13)]
    for month in months:
        # Get the start date and end date of a given yearmonth.
        yearmonth = "{:04d}{:02d}".format(int(year), month)
        startdate, enddate = month_range(yearmonth)
        startdate = startdate.strftime("%Y%m%d")
        enddate = enddate.strftime("%Y%m%d")
        composite_basename = "MTC_{startdate}_{enddate}_{sitecode}_SAR.tif"
        composite_basename = composite_basename.format(startdate=startdate, enddate=enddate, sitecode=sitecode)
        composite_path = None
        for archive_root in archive_roots:
            base_dir = archive_root.joinpath(str(year), countrycode, sitecode, "MTC", "SAR")
            log.debug("Searching for {:s} at {:s}".format(composite_basename, str(base_dir)))
            composite_path = base_dir.joinpath(composite_basename)
            if composite_path.is_file():
                log.debug("Found {:s}".format(str(composite_path)))
                break
        if composite_path is None:
            log.warning("No SAR composite for sitecode={:s}, yearmonth={:s} found.".format(sitecode, yearmonth))
        composite_filepaths.append(composite_path)
    if len(composite_filepaths) != 12:
        raise Exception("Some SAR composites are missing for sitecode={:s} and year={:s}. Expected count is 12, number of found composites is {:d}."
                        .format(sitecode, str(year), len(composite_filepaths)))
    return composite_filepaths


def copy_file_from_s3(s3path, dstpath, retries, timeout, sleep_time):
    # FIXME use better mapping of object name from the mapped S3 path.
    object_name = str(s3path).replace("/s3archive/", "")
    if not object_name.startswith("output"):
        object_name = "output/" + object_name

    cmd = ["swift", "download",
           "--output", str(dstpath),
           "cop4n2k-archive", str(object_name)]
    downloaded = False
    try:
        log.debug(" ".join(cmd))
        subprocess.run(cmd, timeout=timeout, check=True)
        downloaded = True
        log.info("Downloaded cop4n2k-archive:{} to {}".format(object_name, dstpath))
    except Exception as ex:
        log.warning(str(ex))
        for retry in range(retries):
            log.warning("retrying download after {}s ..".format(sleep_time))
            time.sleep(sleep_time)
            try:
                log.debug(" ".join(cmd))
                subprocess.run(cmd, timeout=timeout, check=True)
                log.info("Downloaded cop4n2k-archive:{} to {}".format(object_name, dstpath))
                downloaded = True
                break
            except Exception as ex:
                log.warning(str(ex))
                continue
    if downloaded:
        return dstpath
    else:
        log.warning("Object cop4n2k-archive:{} could not be downloaded.".format(object_name))
        return None


def locate_lulc_geopackage(archive_roots, year, sitecode, postfix):
    if year < 2012:
        reference_geometry = "N2K2006"
    elif year < 2019:
        reference_geometry = "N2K2012"
    else:
        reference_geometry = "N2K2018"
    countrycode = sitecode[0:2]
    gpkg_file = None

    # Input GeoPackage can be with or without an _orig.gpkg postfix.
    if postfix is None:
        gpkg_name = "LULC_{:d}_{:s}_{:s}.gpkg".format(year, reference_geometry, sitecode)
    else:
        gpkg_name = "LULC_{:d}_{:s}_{:s}_{:s}.gpkg".format(year, reference_geometry, sitecode, postfix)

    site_relpath = Path(str(year)).joinpath(countrycode, sitecode, "LULC")
    for archive_root in archive_roots:
        site_dirpath = Path(archive_root).joinpath(site_relpath)
        log.debug("Searching for LULC GeoPackage at {:s}".format(str(site_dirpath)))
        gpkg_file = site_dirpath.joinpath(gpkg_name)
        if gpkg_file.is_file():
            log.info("Found LULC GeoPackage at {:s}".format(str(gpkg_file)))
            break
        gpkg_file = None
    if gpkg_file is None:
        msg = "There is no LULC geopackage for the year {} and sitecode {}. Expected file {} does not exist."
        msg = msg.format(year, sitecode, gpkg_name)
        log.error(msg)
        raise FileNotFoundError(msg)
    return gpkg_file


def locate_lulc_raster(archive_roots, year, sitecode):
    if year < 2015:
        raster_suffix = "OPT_CLASS_POST"
    else:
        raster_suffix = "INT_CLASS_POST"
    countrycode = sitecode[0:2]
    lulc_raster_name = "LULC_{:d}_{:s}_{:s}.tif".format(int(year), sitecode, raster_suffix)
    site_relpath = Path(str(year)).joinpath(countrycode, sitecode, "LULC")
    lulc_raster_file = None
    for archive_root in archive_roots:
        site_dirpath = Path(archive_root).joinpath(site_relpath)
        log.debug("Searching for LULC *CLASS_POST raster at {:s}".format(str(site_dirpath)))
        lulc_raster_file = site_dirpath.joinpath(lulc_raster_name)
        if lulc_raster_file.is_file():
            log.info("Found LULC raster at {:s}".format(str(lulc_raster_file)))
            break
        lulc_raster_file = None
    if lulc_raster_file is None:
        msg = "There is no LULC raster for the year {} and sitecode {}. Expected file {} does not exist."
        msg = msg.format(year, sitecode, lulc_raster_name)
        log.error(msg)
        raise FileNotFoundError(msg)
    return lulc_raster_file


def locate_swf_raster(archive_roots, year, sitecode):
    if int(year) < 2020:
        swf_year = 2015
    else:
        swf_year = 2020
    # determine year_dirpath from the current year
    if 1990 <= int(year) < 2000:
        year_dirpath = "1990_1999"
    elif 2000 <= int(year) < 2006:
        year_dirpath = "2000_2005"
    elif 2006 <= int(year) < 2012:
        year_dirpath = "2006_2011"
    elif 2012 <= int(year) <= 2018:
        year_dirpath = "2012_2018"
    else:
        year_dirpath = "2018_2023"
    swf_name = "{sitecode}_swf_{swf_year}_005m_FULL_3035_v012.tif".format(
        sitecode=sitecode, swf_year=swf_year)
    countrycode = sitecode[0:2]
    swf_relpath =Path("Support").joinpath(year_dirpath, countrycode, "swf")
    for archive_root in archive_roots:
        swf_dirpath = Path(archive_root).joinpath(swf_relpath)
        log.debug("Searching for SWF raster at {:s}".format(str(swf_dirpath)))
        swf_file = swf_dirpath.joinpath(swf_name)
        if swf_file.is_file():
            log.info("Found SWF raster at {:s}".format(str(swf_file)))
            break
        swf_file = None
    if swf_file is None:
        raise FileNotFoundError(
            "There is no SWF raster for the year {} and sitecode {}. Expected file {} does not exist."
                .format(year, sitecode, swf_name))
    return swf_file


class satellite_band():
    def __init__(self):
        self.landsat_band_lookup_table = {
            "landsat-9": {
                "coastal_aerosol": "SR_B1",
                "vis-b": "SR_B2",
                "vis-g": "SR_B3",
                "vis-r": "SR_B4",
                "nir": "SR_B5",
                "swir1": "SR_B6",
                "swir2": "SR_B7",
                "pan": "SR_B8",
                "cirrus": "SR_B9",
                "tir-10900": "SR_B10",
                "tir-12000": "SR_B11"
            },
            "landsat-8": {
                "coastal_aerosol": "SR_B1",
                "vis-b": "SR_B2",
                "vis-g": "SR_B3",
                "vis-r": "SR_B4",
                "nir": "SR_B5",
                "swir1": "SR_B6",
                "swir2": "SR_B7",
                "pan": "SR_B8",
                "cirrus": "SR_B9",
                "tir-10900": "SR_B10",
                "tir-12000": "SR_B11"
            },
            "landsat-7": {
                "vis-b": "SR_B1",
                "vis-g": "SR_B2",
                "vis-r": "SR_B3",
                "nir": "SR_B4",
                "swir1": "SR_B5",
                "swir2": "SR_B7",
                "tir-11450": "SR_B6"
            },
            "landsat-5": {
                "vis-b": "SR_B1",
                "vis-g": "SR_B2",
                "vis-r": "SR_B3",
                "nir": "SR_B4",
                "swir1": "SR_B5",
                "swir2": "SR_B7",
                "tir_11450": "SR_B6"
            },
            "landsat-4": {
                "vis_b": "SR_B1",
                "vis_g": "SR_B2",
                "vis_r": "SR_B3",
                "nir": "SR_B4",
                "swir1": "SR_B5",
                "swir2": "SR_B7",
                "tir_11450": "SR_B6"
            }
        }
        self.sentinel2_band_lookup_10m_table = {"vis-b": "B02_10m",
                                 "vis-g": "B03_10m",
                                 "vis-r": "B04_10m",
                                 "nir": "B08_10m"}

        self.sentinel2_band_lookup_20m_table = {"vis-b": "B02_20m",
                                 "vis-g": "B03_20m",
                                 "vis-r": "B04_20m",
                                 "re-705": "B05_20m",
                                 "re-740": "B06_20m",
                                 "re-781": "B07_20m",
                                 "nir": "B8A_20m",
                                 "swir1": "B11_20m",
                                 "swir2": "B12_20m"
                                 }

    def landsat_band_lookup(self, sat_label, band_label):
        return self.landsat_band_lookup_table[sat_label][band_label]

    def sentinel2_band_lookup(self, band_label, resolution):
        if resolution >= 20:
            band_expr = self.sentinel2_band_lookup_20m_table[band_label]
        else:
            try:
                band_expr = self.sentinel2_band_lookup_10m_table[band_label]
            except KeyError:
                band_expr = self.sentinel2_band_lookup_20m_table[band_label]

        return band_expr

    def satellite_band_check(self, band_label, satellites, resolution=20):
        for sat in satellites:
            if sat.startswith("landsat"):
                 if not band_label in self.landsat_band_lookup_table[sat].keys():
                    log.warning("{} doesnot have data for band {}".format(sat, band_label))
            elif sat.startswith("sentinel"):
                 if band_label in self.sentinel2_band_lookup_10m_table.keys() or self.sentinel2_band_lookup_20m_table.keys():
                    log.debug("{} has data for band {}".format(sat, band_label))
                 else:
                    log.warning("{} doesnot have data for band {}".format(sat, band_label))

    def satellite_bandlist_check(self, bandlist, satellites, resolution = 20):
        for band_label in bandlist:
            self.satellite_band_check(band_label, satellites, resolution)
