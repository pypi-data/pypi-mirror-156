import setuptools

with open("C:\\Users\\ak080\\desktop\\gprmc\\README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()
    print(long_description)

setuptools.setup(
    name = "GPRMC",
    version = "0.0.2",
    author = "arunkumar",
    author_email = "ak080495@gmail.com",
    description = "convert gprmc data",
    long_description = long_description,
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