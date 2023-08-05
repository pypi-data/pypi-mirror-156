import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mrfdictionary",
    version="0.0.2",
    author="Andrew Dupuis",
    author_email="andrewpdupuis@gmail.com",
    description="Tools for MRF dictionary simulation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'jsonpickle',
        'numba',
        'scipy',
        'h5py'
    ]   
)