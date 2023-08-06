# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
  name = 'c1algo1demo',
  packages = ['c1algo1demo'],
  version = '1.0.3',
  license='MIT',
  description = 'scheduler algo!',
  author = 'SENG499 Company 1 - Algo 1',
  author_email = 'benjaminaustin@uvic.ca',
  url = 'https://github.com/seng499-company1/algorithm-1',
  python_requires='>=3.10',
  install_requires=[
          'treelib',
          'twine',
          'bump',
      ]
)