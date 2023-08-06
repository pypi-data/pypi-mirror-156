from setuptools import setup, find_packages
import glob
import os
import sys

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('ecli/plugins')

required_packages = [
        'bs4>=0.0.1,<0.1',
        'click>=8.0,<9.0',
        'click-plugins>=1.1.1,<1.2',
        'colorama>=0.4.3,<0.5',
        'first>=2.0.2,<2.1',
        'bertdotconfig>=4.2.0,<4.3.0',
        'paramiko>=2.7.0,<2.8',
        'jello>=1.2.10,<1.3',
        'requests>=2.22.0,<2.23',
        'PyYAML>=5.3.1,<6.0',
    ]

if '--show-packages' in ' '.join(sys.argv):
    for p in required_packages:
        print(p.split('=')[0])
    sys.exit()    

setup(
    name='bertdotecli',
    version='1.6.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=required_packages,
    package_data={'': extra_files},
    entry_points='''
        [core_package.cli_plugins]
        [console_scripts]
        ecli=ecli.cli:cli
    ''',
)