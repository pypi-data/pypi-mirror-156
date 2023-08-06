from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='jamesmoon_world',
    version='0.0.1',
    description='Say hello!',
    py_modules=["helloworld"],
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Install requires will have production dependencies (flask, numpy, pandas)
    # put relaxed versions
    # install_requires = {
    #     "blessings ~= 1.7"
    # },
    # Extras requires are optional requirements; be more specific
    extras_require = {
        "dev": [
            "pytest>=3.7",
        ],
    },
    url="https://github.com/moonchangin/helloworld_pypi",
    author="Chang In Moon",
    author_email="changin.moon@bcm.edu",
)