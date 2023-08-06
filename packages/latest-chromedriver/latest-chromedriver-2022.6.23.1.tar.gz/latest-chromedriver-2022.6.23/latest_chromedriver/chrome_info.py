import os
import platform
import re
import shutil
import subprocess
from functools import lru_cache

import ubelt as ub
from logzero import logger

VERSION_OUTPUT_RE = r".*?(\d+\.\d+\.\d+\.\d+).*"


@lru_cache(maxsize=None)
def _get_chrome_executable():
    system_name = platform.system()
    if system_name == 'Windows':
        return "chrome.exe"
    if system_name == 'Linux':
        return "google-chrome"
    return None


def _windows_program_locations():
    possible_folders = [os.environ.get(
        i) for i in ["ProgramFiles(x86)", "ProgramW6432"]]
    possible_folders.append(str(ub.Path.home()))
    for folder in possible_folders:
        if folder:
            logger.debug(f"Searching in: {folder}")
            yield folder


def _is_exe(fpath):
    return os.path.exists(fpath) and os.access(fpath, os.X_OK) and os.path.isfile(fpath)


@lru_cache(maxsize=None)
def get_path():
    logger.debug("Searching for Google Chrome installations...")
    system_name = platform.system()
    search_filename = _get_chrome_executable().casefold().strip()
    in_path = shutil.which(search_filename)
    if in_path:
        return in_path

    if system_name == 'Windows':
        for folder in _windows_program_locations():
            for root, dirs, files in os.walk(folder):
                for filename in files:
                    if filename.casefold() == search_filename:
                        filepath = os.path.join(root, filename)
                        if _is_exe(filepath):
                            return filepath
    logger.error("Google Chrome wasn't found in the usual locations")
    return None


@lru_cache(maxsize=None)
def get_version():
    version = None
    system_name = platform.system()
    chrome_path = get_path()
    if system_name == 'Windows':
        output = subprocess.check_output(
            'powershell -command "&{(Get-Item \'%s\').VersionInfo.ProductVersion}"' % (chrome_path), shell=True)
    else:
        output = subprocess.check_output(
            '%s --version' % (chrome_path), shell=True)
    output_str = output.decode(encoding='ascii')
    for match in re.finditer(VERSION_OUTPUT_RE, output_str, re.MULTILINE):
        version = match.group(1)
    logger.debug(f"Google Chrome Version: {version}")
    return version
