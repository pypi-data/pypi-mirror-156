import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="riimut",
    version="1.1.0",
    author="stscoundrel",
    description="Transform latin letters to runes and vice versa",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stscoundrel/riimut-py",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9",
)
