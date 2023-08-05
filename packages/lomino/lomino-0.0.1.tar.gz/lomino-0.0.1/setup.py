import pathlib
from setuptools import setup, find_packages
README = (pathlib.Path(__file__).parent / "README.md").read_text()
setup(name="lomino",version="0.0.1",url="https://github.com/L0Rd5/lomino",download_url="https://github.com/L0Rd5/lomino/archive/refs/heads/main.zip",description="Amino library",long_description=README,long_description_content_type="text/markdown",author="Lord",author_email="lordzero106@gmail.com",license="MIT",keywords=["amino","python","lomino","python3.x","lord","L0Rd5"],include_package_data=True,install_requires=[
        "JSON_minify",
        "setuptools",
        "requests"],setup_requires=["wheel"],packages=find_packages(),)