"""Function used to extract package information from a local setup.py"""

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

    # import you setup.py with mocked setup()
    from . import setup

    return package_metadata


def get_setup_metadata(key: str):
    """Get value of a specific parameter of setup()"""
    package_metadata = extract_setup_metadata()
    return package_metadata[key]
