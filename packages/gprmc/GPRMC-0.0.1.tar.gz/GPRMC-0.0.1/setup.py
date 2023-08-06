import setuptools

# with open("README.md", "r", encoding = "utf-8") as fh:
#     long_description = fh.read()

setuptools.setup(
    name = "GPRMC",
    version = "0.0.1",
    author = "arunkumar",
    author_email = "ak080495@gmail.com",
    description = "convert gprmc data",
    long_description = "long_description",
    long_description_content_type = "text/markdown",
    url = "https://gitlab.com/ak080495/gprmc",
    project_urls = {
        "Bug Tracker": "https://gitlab.com/ak080495/gprmc/-/issues",
        
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    python_requires = ">=3.6"
)