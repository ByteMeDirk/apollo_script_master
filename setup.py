from setuptools import setup, find_packages

setup(
    name='apollo_script_master',
    version='0.0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            '_asm = apollo_script_master:main',
            'apollo_script_master = apollo_script_master:main'
        ],
    },
)
