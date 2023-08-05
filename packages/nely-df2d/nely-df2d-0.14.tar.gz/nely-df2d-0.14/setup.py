from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="nely-df2d",
    version="0.14",
    packages=["df2d"],
    author="Semih Gunel",
    author_email="gunelsemih@gmail.com",
    description="2D pose estimation pipeline for tethered Drosophila.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NeLy-EPFL/Drosophila2DPose",
)
