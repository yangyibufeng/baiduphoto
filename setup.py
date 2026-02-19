"""
Setup script for pybaiduphoto.

Run: pip install .
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_file(filename):
    """Read file contents."""
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, filename), encoding='utf-8') as f:
        return f.read()

# Read version from __init__.py
def get_version():
    """Get version from package __init__.py"""
    version_file = os.path.join('pybaiduphoto', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '0.0.0'

setup(
    name='pybaiduphoto',
    version=get_version(),
    author='HengyueLi',
    author_email='your.email@example.com',
    description='A Python library for Baidu Photo (一刻相册) API',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/HengyueLi/baiduphoto',
    project_urls={
        'Bug Reports': 'https://github.com/HengyueLi/baiduphoto/issues',
        'Source': 'https://github.com/HengyueLi/baiduphoto',
        'Documentation': 'https://github.com/HengyueLi/baiduphoto/blob/main/README.md',
    },
    packages=find_packages(exclude=['tests', 'tests.*', 'examples', 'examples.*']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=[
        'requests>=2.22.0',
        'rich>=10.16.1',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ],
        'browser': [
            'browser-cookie3>=0.19.0',
        ],
    },
    keywords='baidu photo api album upload download',
    license='MIT',
    zip_safe=False,
    include_package_data=True,
)