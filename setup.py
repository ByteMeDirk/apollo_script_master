from setuptools import setup, find_packages

# Get requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Get long description from README.md
with open('README.md') as f:
    long_description = f.read()

setup(
    name='apollo_script_master',
    version='0.0.1',
    description='ApolloScriptMaster is an ORM solution designed for seamless management of SQL scripts within a CiCd deployment strategy.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='ByteMeDirk',
    author_email='bytemedirk@proton.me',
    maintainer='ByteMeDirk',
    maintainer_email='bytemedirk@proton.me',
    url='https://github.com/ByteMeDirk/apollo_script_master',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'asm = apollo_script_master:main',
            'apollo_script_master = apollo_script_master:main'
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
