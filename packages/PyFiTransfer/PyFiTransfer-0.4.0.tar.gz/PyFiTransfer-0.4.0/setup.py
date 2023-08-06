import pathlib
from setuptools import setup, find_packages

readme = pathlib.Path("readme.md").read_text()
reqs = pathlib.Path("requirements.txt").read_text()
setup(
    name="PyFiTransfer",
    version="0.4.0",
    description=
    'Transfer files with specified extension-type from a starting directory to desired target directory.',
    url='https://github.com/schlopp96/PyFiTransfer',
    author='schlopp96',
    author_email='schloppdaddy@gmail.com',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[reqs],
    entry_points={
        'gui_scripts': ['pyfitransfer-gui=PyFiTransfer.main:main'],
        'console_scripts': ['pyfitransfer-cli=PyFiTransfer.CLI_main:CLI_main']
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    keywords=[
        'file', 'transfer', 'script', 'files', 'directory', 'directories',
        'extension', 'extensions', 'rename-files', 'rename-file', 'move-file',
        'move-files'
    ])
