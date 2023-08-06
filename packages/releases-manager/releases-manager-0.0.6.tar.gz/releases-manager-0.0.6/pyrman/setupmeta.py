"""Function used to extract package information from a local setup.py"""
import os
import sys


def extract_setup_metadata():
    """Get all values of parameters passed to setup()"""
    import distutils.core
    import setuptools

    package_metadata = {}

    def on_setup_loaded(**metadata):
        package_metadata.update(metadata)

    # mock setup functions to only print package name
    setuptools.setup = on_setup_loaded
    distutils.core.setup = on_setup_loaded

    # make sure we will be able to import setup from current directory
    current_directory = os.getcwd()
    sys.path.insert(0, current_directory)

    # import you setup.py with mocked setup()
    print('Loading setup from directory', current_directory, file=sys.stderr)
    import setup

    return package_metadata


def get_setup_metadata(key: str):
    """Get value of a specific parameter of setup()"""
    package_metadata = extract_setup_metadata()
    value = package_metadata[key]
    print(f'Value for key {key} in setup is {value}', file=sys.stderr)
    return value
