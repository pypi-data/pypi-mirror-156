"""
    serialid
    ~~~~
    Sequential Unique Short & Sortable Identifier
    :copyright: (c) 2022 Faraz Khan.
    :license: MIT, see LICENSE for more details.
"""
import ast
import re

try:
    from setuptools import find_packages, setup
except ImportError:
    from distutils.core import setup


version_regex = re.compile(r'__version__\s+=\s+(.*)')


def get_version():
    with open('serialid/__init__.py', 'r') as f:
        return str(ast.literal_eval(version_regex.search(f.read()).group(1)))


def get_long_description():
    with open('README.md') as f:
        return f.read()


setup(
    name='serial-id',
    version=get_version(),
    author='Faraz Khan',
    author_email='mk.faraz@gmail.com',
    url='https://github.com/mysteryjeans/serial-id',
    download_url='https://github.com/mysteryjeans/serial-id/archive/refs/tags/v-0.1.tar.gz',
    license='MIT License',
    description='Sequential Unique Short & Sortable Identifier',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    package_data={'serialid': ['py.typed']},
    zip_safe=False,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules'
    )
)