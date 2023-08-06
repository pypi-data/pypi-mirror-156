
from setuptools import setup

with open("README.md") as fh:
    long_desc = fh.read()

setup(
    name='hjklhjkvv',
    version='5.0',
    description='---------',
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url='https://github.com/xvfgc/hjklhjkvv',
    license='MIT',
    author='xvfgc',
    packages=['hjklhjkvv'],
    package_data={
        'hjklhjkvv': ['py.typed'],
    },
    install_requires=[
        'numpy',
    ],
    zip_safe=False,
    python_requires='>=3.10',
)
