__author__ = 'ettore'
__version__ = (0, 0, 0)

import os

from setuptools import setup, find_packages


def parse_requirements(filename):
    with open(filename) as f:
        lines = f.readlines()
        striped_lines = filter(None, map(str.strip, lines))
        true_requirements = filter(lambda s: not s.startswith('#'), striped_lines)
        return list(true_requirements)


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


requirements = []
str_version = '.'.join(map(str, __version__))

setup(
    name='py-shared',
    version=str_version,
    description='Python Shared',
    long_description=read('README.rst'),
    url='https://github.com/ettoreleandrotognoli/python-shared',
    download_url='https://github.com/ettoreleandrotognoli/python-shared/tree/%s/' % str_version,
    license='BSD',
    author=u'Éttore Leandro Tognoli',
    author_email='ettore.leandro.tognoli@gmail.com',
    packages=find_packages(where='./src', exclude=['tests', 'examples']),
    package_dir={'': 'src'},
    include_package_data=True,
    keywords=[],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: BSD License',
    ],
    install_requires=parse_requirements('requirements.txt'),
    tests_require=parse_requirements('requirements-dev.txt'),
)
