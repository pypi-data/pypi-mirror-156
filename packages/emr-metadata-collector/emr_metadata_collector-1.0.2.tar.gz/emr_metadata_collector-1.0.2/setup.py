from setuptools import setup, find_packages

setup(
    name='emr_metadata_collector',
    version='1.0.2',
    author="Jianwei Li",
    author_email="lijianwe@amazon.com",
    description="EMr metadata collector for operational review",
    scripts=['emr_metadata_collector'],
    packages=find_packages(),
    package_data={
        "": ["*.yml"],
    },
    install_requires=[
        "requests",
        "requests-aws4auth",
        "boto3",
        "pyyaml"
    ],
 )