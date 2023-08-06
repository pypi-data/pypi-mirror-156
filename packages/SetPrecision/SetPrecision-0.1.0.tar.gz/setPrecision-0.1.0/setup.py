import pathlib
from setuptools import setup, find_packages

readme = pathlib.Path("readme.md").read_text()
reqs = pathlib.Path("requirements.txt").read_text()
setup(
    name="setPrecision",
    version="0.1.0",
    description=
    "`setPrecision` is a small module providing a simple way to set the precision of a floating point number or decimal to the desired amount of significant digits.",
    url='https://github.com/schlopp96/setPrecision',
    author='schlopp96',
    author_email='schloppdaddy@gmail.com',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[reqs],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Utilities",
    ],
    keywords=[
        'setPrecision', 'float', 'decimal', 'precision', 'sig', 'figs',
        'significant', 'digits', 'scientific', 'notation', 'math',
        'conversion', 'script', 'point', 'floating'
    ])
