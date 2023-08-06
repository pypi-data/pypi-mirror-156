import setuptools
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def read(rel_path: str) -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with open(os.path.join(here, rel_path)) as fp:
        return fp.read()


def get_version(rel_path: str) -> str:
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            # __version__ = "0.9"
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name="polaritymodel",
    version=get_version("src/polaritymodel/__init__.py"),
    author="Jordan Snyder",
    author_email="snydrew@gmail.com",
    description="A package for running the cell polarity model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jasnyder/polarpkg",
    project_urls={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    install_requires=[
        'torch',
        'torchaudio',
        'torchvision',
        'numpy',
        'scipy',
        'plotly',
        'pandas'
    ],
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)