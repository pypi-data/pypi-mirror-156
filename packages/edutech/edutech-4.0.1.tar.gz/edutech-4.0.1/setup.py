from setuptools import setup

setup(
    name="edutech",
    version='4.0.1',
    description="this is my module",
    long_description='long description',
    author="praveen kumar",
    packages=['edutech'],
    )
# python setup.py sdist bdist_wheel
# twine upload dist/*
# twine upload --skip-existing dist/*