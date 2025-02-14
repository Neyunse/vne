# setup.py
import os

import setuptools

about = {}
with open("vne/_version.py") as f:
    exec(f.read(), about)

os.environ["PBR_VERSION"] = about["__version__"]

setuptools.setup(
    setup_requires=["pbr"],
    pbr=True,
    version=about["__version__"],
)