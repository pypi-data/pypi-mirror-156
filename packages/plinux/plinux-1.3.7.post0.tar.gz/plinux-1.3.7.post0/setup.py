from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='plinux',
    version='1.3.7post0',
    packages=['plinux'],
    url='https://github.com/c-pher/plinux',
    license='GNU General Public License v3.0',
    author='Andrey Komissarov',
    author_email='a.komisssarov@gmail.com',
    description='The cross-platform tool to execute bash commands remotely.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'paramiko>=2.11.0', 'plogger>=1.0.6', 'python-dateutil>=2.8.1'
    ],
    python_requires='>=3.9',
)
