from setuptools import setup

setup(name="tassistant",
    version="1.0.2",
    packages=['tassistant'],
    package_data={
        "tassistant": ["tassistant.py", "city.py", "tictactoe.py"],
    },
)