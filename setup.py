from setuptools import setup, find_packages

def get_requirements():
    return open("requirements.txt").read().split("\n")

setup(name="taggo",
      version="0.7",
      packages=find_packages(exclude=('tests', 'docs')),
      author="sourcepirate",
      test_suite='tests',
      include_package_data=True,
      install_requires=get_requirements(),
      scripts=['bin/taggo'])