import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django-questionnaire",
    version = "0.0.1",
    author = "Jason Marshall, John Allen, Zaim Dolrani, Ayoola Adegbite, Pandu Purbasany ",
    author_email = "j.j.marshall [at] kent.ac.uk",
    description = ("A django application for creating reusable web questionnaires"),
    license = "MIT",
    keywords = "django questionnaire survry",
    url = "http://pypi.python.org/pypi/django-questionnaire/0.01",
    packages=['django-questionnaire',],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=['django']
)
