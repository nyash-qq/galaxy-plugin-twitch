import glob
import json
import os
import platform
from collections import namedtuple
from shutil import copy, copytree, rmtree

from invoke import task

with open(os.path.join("src", "manifest.json"), "r") as manifest:
    _MANIFEST = json.load(manifest, object_hook=lambda d: namedtuple("MANIFEST", d.keys())(*d.values()))

_LOCAL_APPDATA = {
    "Windows": os.path.expandvars("%LOCALAPPDATA%")
    , "Darwin": os.path.join(os.path.expandvars("$HOME"), "Library", "Application Support")
}[platform.system()]

_INSTALL_PATH = os.path.join(
    _LOCAL_APPDATA, "GOG.com", "Galaxy", "plugins", "installed", f"{_MANIFEST.platform}_{_MANIFEST.guid}"
)

_OUTPUT_DIR = "output"
_PLATFORM = {
    "Windows": "win32"
    , "Darwin": "macosx_10_12_x86_64"
}[platform.system()]
_REQ_DEV = "requirements.txt"
_REQ_RELEASE = "requirements-release.txt"


@task(aliases=["r", "req"])
def requirements(ctx):
    ctx.run(f"pip install -r {_REQ_DEV}")


@task(requirements, aliases=["t"])
def test(ctx):
    ctx.run("pytest")


@task(test, aliases=["b"])
def build(ctx, output_dir=_OUTPUT_DIR):
    if os.path.exists(output_dir):
        rmtree(output_dir)

    ctx.run(
        "pip install"
        f" -r {_REQ_RELEASE}"
        f" --platform {_PLATFORM}"
        f" --target {output_dir}"
        " --python-version 37"
        " --only-binary=:all:"
        , echo=True
    )

    [copy(src, output_dir) for src in glob.glob("src/*.*")]

    [rmtree(dir_) for dir_ in glob.glob(f"{output_dir}/*.dist-info")]


@task(build)
def install(ctx, src_dir=_OUTPUT_DIR):
    print(f"Installing into: {_INSTALL_PATH}")
    if os.path.exists(_INSTALL_PATH):
        rmtree(_INSTALL_PATH)

    copytree(src_dir, _INSTALL_PATH)


@task(aliases=["p"])
def pack(ctx, output_dir=_OUTPUT_DIR):
    from galaxy.tools import zip_folder_to_file

    build(ctx, output_dir=output_dir)
    zip_folder_to_file(
        output_dir
        , f"{_MANIFEST.platform}_{_MANIFEST.guid}_v{_MANIFEST.version}_{_PLATFORM}.zip"
    )
