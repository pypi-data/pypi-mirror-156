from setuptools import setup, find_packages
from citerate.version import __version__

setup(
    name="citerate",
    version=__version__,
    description="A Python bi-dimensional matrix iterator starting from any point (i, j), going layer by layer around the starting coordinates.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/markmelnic/citerate",
    author="Mark Melnic",
    author_email="me@markmelnic.com",
    license="MIT",
    python_requires='==3.*',
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    zip_safe=False,
    include_package_data=True,
    install_requires=[],
    entry_points={"console_scripts": []},
)
