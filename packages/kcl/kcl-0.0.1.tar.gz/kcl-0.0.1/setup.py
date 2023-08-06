import pathlib

from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

with open(HERE / "README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kcl",
    packages=["kaiyo", "kaiyo.modules", "kaiyo.utils"],
    package_data={'kaiyo': ['*'], 'kaiyo.modules': ['*'], 'kaiyo.utils': ['*']},
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": ['kaiyo = kaiyo.kaiyo:kaiyo']
    },
    version="0.0.1",
    description="Kaiyo.dev Cloud CLI",
    author="Kaiyo Engineering Team",
    author_email="engineering@kaiyo.dev",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
)

'''
python3 -m venv env
source env/bin/activate
python3 -m pip install --editable .




python3 setup.py sdist
twine upload dist/*
'''
