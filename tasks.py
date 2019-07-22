import glob
import json
import os
import platform
import tempfile
from shutil import copy, copytree, rmtree

from galaxy.tools import zip_folder_to_file
from invoke import task

with open(os.path.join("src", "manifest.json"), "r") as manifest:
    _MANIFEST = json.load(manifest)

_LOCAL_APPDATA = {
    "Windows": os.path.expandvars("%LOCALAPPDATA%")
    , "Darwin": os.path.join(os.path.expandvars("$HOME"), "Library", "Application Support")
}[platform.system()]

_INSTALL_PATH = os.path.join(
    _LOCAL_APPDATA, "GOG.com", "Galaxy", "plugins", "installed", "{platform}_{plugin_id}".format(
        platform=_MANIFEST["platform"], plugin_id=_MANIFEST["guid"]
    )
)

_OUTPUT_DIR = "output"
_PLATFORM = {
    "Windows": "win32"
    , "Darwin": "macosx_10_12_x86_64"
}[platform.system()]
_REQ_DEV = "requirements.txt"
_REQ_RELEASE = "requirements-release.txt"
_VERSION = _MANIFEST["version"]


@task(aliases=["r", "req"])
def requirements(ctx):
    ctx.run("pip install -r {}".format(_REQ_DEV))


@task(requirements, aliases=["t"])
def test(ctx):
    ctx.run("pytest")


@task(test, aliases=["b"])
def build(ctx, output_dir=_OUTPUT_DIR):
    if os.path.exists(output_dir):
        rmtree(output_dir)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
        ctx.run("pip-compile {req} --dry-run".format(req=_REQ_RELEASE), out_stream=tmp)
        ctx.run(
            "pip install"
            " -r {req}"
            " --platform {platform}"
            " --target {output_dir}"
            " --python-version 37"
            " --no-compile"
            " --no-deps".format(req=tmp.name, platform=_PLATFORM, output_dir=output_dir)
            , echo=True
        )

    [copy(src, output_dir) for src in glob.glob("src/*.*")]

    [rmtree(dir_) for dir_ in glob.glob("{}/*.dist-info".format(output_dir))]


@task(build)
def install(ctx, src_dir=_OUTPUT_DIR):
    print("Installing into: {}".format(_INSTALL_PATH))
    if os.path.exists(_INSTALL_PATH):
        rmtree(_INSTALL_PATH)

    copytree(src_dir, _INSTALL_PATH)


@task(aliases=["p"])
def pack(ctx, output_dir=_OUTPUT_DIR):
    build(ctx, output_dir=output_dir)
    zip_folder_to_file(
        output_dir
        , "{plugin_platform}_{plugin_id}_v{version}_{os}.zip".format(
            plugin_platform=_MANIFEST["platform"]
            , plugin_id=_MANIFEST["guid"]
            , version=_MANIFEST["version"]
            , os=_PLATFORM
        )
    )
