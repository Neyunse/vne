from setuptools import setup, find_packages
import pathlib
from vne import __version__ as version


here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8") if (here / "README.md").exists() else "Visual Novel Engine."

# Solo dependencias esenciales del motor
engine_requirements = [
    "pygame-ce",
    "pyinstaller",
    "pyzipper",
    "cryptography",
    "Pillow",
    "PyQt6"
]

setup(
    name="vne",
    version=version,
    description="Visual Novel Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Neyunse",
    url="https://github.com/Neyunse/vne",
    packages=find_packages(),
    install_requires=engine_requirements,
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
