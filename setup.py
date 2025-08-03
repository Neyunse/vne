from setuptools import setup, find_packages
import pathlib
from vne._version import __version__

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8") if (here / "README.md").exists() else "Visual Novel Engine."
requirements = []

import re
with open("requirements.txt", "rb") as f:
    requirements = []
    for line in f:
        try:
            decoded = line.decode("utf-8").strip()
        except UnicodeDecodeError:
            decoded = line.decode("utf-8", errors="ignore").strip()
        # Solo líneas válidas: letras, números, guiones, puntos, >=, <=, ==, etc.
        if decoded and not decoded.startswith('#'):
            cleaned = re.sub(r'[^a-zA-Z0-9_\-.>=<, ]', '', decoded)
            if cleaned:
                requirements.append(cleaned)

setup(
    name="vne",
    version=__version__,
    license="MIT",
    description="Visual Novel Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Neyunse",
    url="https://github.com/Neyunse/vne",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "vne=main:main"
        ]
    },
    keywords=["visual novel", "engine", "pygame", "pyinstaller"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ],
)
