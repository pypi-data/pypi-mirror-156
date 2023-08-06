import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tlsfeatmark",
    version="0.1",
    author="Zhi Liu",
    author_email="zliucd66@gmail.com",
    description="a benchmark tool for Joy and Zeek",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zliucd/tlsfeatmark",
    packages=setuptools.find_packages(),
    install_requires=['py-cpuinfo>=8.0.0'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)