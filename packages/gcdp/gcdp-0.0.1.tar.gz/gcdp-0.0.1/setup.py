import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gcdp",
    version="0.0.1",
    author="GC",
    author_email="yejinjo@gccorp.com",
    description="gcdp",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ojjy/gcdp",
    project_urls={
        "Bug Tracker": "https://github.com/ojjy/gcdp/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src", exclude=["*.sql", "*.SQL", "*.json", "*.csv", "*downloads*", "tests"]),
    python_requires=">=3.8",
)