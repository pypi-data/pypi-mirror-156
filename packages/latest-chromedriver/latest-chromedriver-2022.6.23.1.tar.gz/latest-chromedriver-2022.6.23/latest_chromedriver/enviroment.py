import os

from logzero import logger

from . import download_driver


def _clean_and_add_env_path(add_path):
    cleaned_path = []
    # Clean the already defined path
    abs_path = [os.path.abspath(x)
                for x in os.environ['PATH'].split(os.pathsep)]

    for c_path in abs_path:
        if (c_path and (c_path.casefold() not in [x.casefold() for x in cleaned_path])):
            cleaned_path.append(c_path)

    # Add the new paths in the start of the path
    if add_path:
        add_path = os.path.abspath(add_path)
        add_path_case = add_path.casefold()
        for c_path in cleaned_path[:]:
            if add_path_case == c_path.casefold():
                cleaned_path.remove(c_path)
        cleaned_path.insert(0, add_path)

    os.environ['PATH'] = os.pathsep.join(cleaned_path)


def safely_set_chromedriver_path():
    chromedriver_path = download_driver.download_only_if_needed()
    logger.debug(f"Adding {chromedriver_path} to PATH")
    _clean_and_add_env_path(chromedriver_path)
