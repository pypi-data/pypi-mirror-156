from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
    fh.close()

with open("requirements.txt", "r") as fh:
    requirements = fh.read()
    fh.close()

VERSION = '1.1.1'

setup(
    name="config_py2",
    version=VERSION,
    author = 'Chalukya',
    author_email = 'chalukya@gmail.com',
    license = 'MIT',
    description = 'A Config Management Tool similar to dynaconf for python >= 2.7',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://gitlab.com/chalukyaj/config-manager-python2",
    project_urls = {
        "Bug Tracker": "https://gitlab.com/chalukyaj/config-manager-python2/issues"
    },
    keywords=["config", "toml", "json", "yaml", "dynaconf"],
    install_requires=[requirements],
    packages=['config_py2'],
    python_requires='>=2.7',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Documentation',
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": ["config_py2 = config_py2.config_entrypoint:entrypoint"]},
)
