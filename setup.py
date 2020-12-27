import os

import setuptools


def local_file(name):
    return os.path.relpath(os.path.join(os.path.dirname(__file__), name))


SOURCE = local_file("src")
README = local_file("README.rst")

setuptools_version = tuple(map(int, setuptools.__version__.split(".")[:2]))

# Assignment to placate pyflakes. The actual version is from the exec that
# follows.
__version__ = None

with open(local_file("src/omnimetrics/_version.py")) as o:
    exec(o.read())

assert __version__ is not None

setuptools.setup(
    name="omnimetrics",
    version=__version__,
    author="Jonathan M. Lange",
    author_email="jml@mumak.net",
    packages=setuptools.find_packages(SOURCE),
    package_dir={"": SOURCE},
    url=("https://github.com/jml/omnimetrics/"),
    license="Apache",
    description="Tools for exploring OmniFocus 3 data",
    zip_safe=False,
    install_requires=["appscript", "click", "dbt", "google-cloud-bigquery", "google-cloud-storage", "pyobjc"],
    python_requires=">=3.8",
    classifiers=[
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    entry_points={
        "console_scripts": [
            "viewit=omnimetrics._viewit:main",
            "procrastinatron=omnimetrics.__main__:procrastinatron",
            "omnimetrics=omnimetrics._script:omnimetrics",
        ]
    },
    long_description=open(README).read(),
)
