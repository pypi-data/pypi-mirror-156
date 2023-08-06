import pathlib
import setuptools as st
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
setup(
    name="dataoutsider",
    version="1.2.1",
    description="Data visualization toolbox.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/dataoutsider/",
    author="Nick Gerend",
    author_email="nickgerend@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
    ],
    packages=st.find_namespace_packages(),
    install_requires=["pandas", "numpy", "matplotlib"],
    include_package_data=True,
    package_data={'': ['data/*.csv']},
)