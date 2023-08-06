from pathlib import Path
from setuptools import setup
from os import environ

cwd = Path(".")

README = (cwd / "README.md").read_text()
dependencies = (cwd / "requirements.txt").read_text().strip().split("\n")

# This should be set by the automated Github workflow
VERSION = environ["SEMANTIC_VERSION"] if "SEMANTIC_VERSION" in environ else "1.0.0"

setup(
    name="exifstrip",
    version=VERSION,
    description="Remove EXIF data from images.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/bradendubois/exif-strip",
    author="Braden Dubois",
    author_email="braden.dubois@usask.ca",
    packages=["exifstrip"],
    keywords="exif image python",
    include_package_data=True,
    install_requires=dependencies,
    entry_points={
        'console_scripts': ["exifstrip=exifstrip.main:run"],
    }
)
