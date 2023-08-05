import os
import versioneer

from setuptools import setup, find_packages

# read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="cccs",
    version=versioneer.get_version(),
    description="CCCS common python library",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/CybercentreCanada/ccccs_common_python",
    author="CCCS development team",
    author_email="dev@cyber.gc.ca",
    license="MIT",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
    ],
    keywords="gc canada cse-cst cse cst cyber cccs",
    packages=find_packages(exclude=['test', 'test/*']),
    install_requires=[
        'passlib',
        'python-baseconv',
        'PyYAML',
        'elastic-apm[flask]',
        'netifaces',
        'pyroute2.core',
        'requests',
        'elasticsearch>=7.0.0,<8.0.0',
        'python-datemath',
        'redis',
        'packaging',
        'pysftp',
        'boto3',
        'azure-storage-blob',
        'azure-identity',
        'chardet',
    ],
    extras_require={
        'dev': [
            'flake8',
            'autopep8',
        ],
        'test': [
            'pytest',
            'retrying',
            'pyftpdlib',
            'pyopenssl',
        ]
    },
    package_data={
        '': [
            "*classification.yml",
            "VERSION",
        ]
    }
)
