from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "mattsimplecalculator",
    version = "0.0.1",
    author = "Matt Meyer",
    author_email = "matt.meyer3@gmail.com",
    description = ("Basic calculator"),
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    license = "MIT",
    keywords = "calculator",
    url = " ",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)