from pathlib import Path

from setuptools import find_packages, setup

with (Path(__file__).parent / "README.md").open("r") as f:
    readme = f.read()

setup(
    author="Nicolas Cedilnik",
    author_email="nicoco@nicoco.fr",
    description="Fetches publications from HAL",
    keywords="Lektor plugin static-site blog",
    license="MIT",
    long_description=readme,
    long_description_content_type="text/markdown",
    name="lektor-hal",
    packages=find_packages(),
    py_modules=["lektor_hal"],
    url="http://gilab.com/nicocool84/lektor-hal",
    version="0.1.0",
    classifiers=[
        "Framework :: Lektor",
        "Environment :: Web Environment",
        "Environment :: Plugins",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        "lektor.plugins": [
            "hal = lektor_hal:HalPlugin",
        ]
    },
)
