from setuptools import setup

setup(name="tassistant",
    version="1.0.1",
    packages=['tassistant'],
    package_data={
        "tassistant": ["figures.py", "buildings.py", "utilities.py"],
    },
)