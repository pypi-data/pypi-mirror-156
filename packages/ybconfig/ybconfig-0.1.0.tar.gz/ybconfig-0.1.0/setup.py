from setuptools import setup, find_packages
import pathlib


with open('README.md', 'r') as f:
    long_description = f.read()

# with open(str(pathlib.Path(__file__).parent.absolute()) +
#           "/flitton_fib_py/version.py", "r") as fh:
#     version = fh.read().split("=")[1].replace("'", "")


setup(
    name='ybconfig',
    version='0.1.0',
    author='Maxwell Flitton',
    author_email='maxwellflitton@gmail.com',
    packages=find_packages(exclude=("tests",)),
    scripts=[],
    url="https://github.com/yellow-bird-consult/yb_config",
    description='Basic configuration management for YB',
    long_description=long_description,
    long_description_content_type='text/markdown',
    package_data={'': ['script.sh']},
    include_package_data=True,
    install_requires=[
        "pyyaml",
    ],
    entry_points={
        "console_scripts": [
        ]
    },
)
