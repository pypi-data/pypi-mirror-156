import os

import click

from pyrman.client import REPOSITORY_DEFAULT_URL, ReleaseManagerClient
from pyrman.context import context
from pyrman.serialize import serialize_as_yaml
from pyrman.setupmeta import get_setup_metadata


@click.group
@click.option(
    "-u", "--username", default=os.getenv("PYRMAN_USERNAME"), help="Python repository username",
)
@click.option(
    "-p", "--password", default=os.getenv("PYRMAN_PASSWORD"), help="Read python repository password from stdin",
)
@click.option(
    "--url", default=REPOSITORY_DEFAULT_URL, help="Python repository URL (defaults to https://pypi.org)",
)
def cli(username: str, password: str, url: str = None):
    """Python releases manager
    
    Manage python published release for packages that you owns on PyPI
    """
    context.client = ReleaseManagerClient(url)
    if username or password:
        context.client.set_credentials(username, password)


@cli.command
def get_package_root_folder():
    """Get root folder of package located in current folder"""
    print(get_setup_metadata("packages")[0])


@cli.group()
def setup_meta():
    """Commands related to reliably parsing setup.py"""


@setup_meta.command
@click.argument("metadata_name")
def get(metadata_name: str):
    """Get value of metadata passed as argument to setup() in setup.py"""
    print(get_setup_metadata(metadata_name))



@cli.group
def package():
    """Manage packages"""


@package.command
def ls():
    """List owned packages"""
    packages = context.client.get_packages()
    print(serialize_as_yaml(packages))


@cli.group
def release():
    """Manage releases"""


@release.command
@click.argument("package")
def ls(package: str):
    releases = context.client.list_releases(package)
    print(serialize_as_yaml(releases))


@release.command
@click.argument("package")
@click.argument("version")
def rm(package: str, version: str):
    """Remove release"""
    context.client.remove_release(package, version)
