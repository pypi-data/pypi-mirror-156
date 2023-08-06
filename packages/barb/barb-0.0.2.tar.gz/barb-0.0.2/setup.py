from setuptools import setup, find_packages

ld = 'Hassle free git hooks for python projects.'

setup(
    name='barb',
    version='0.0.2',
    author='Jett Crowson',
    author_email='jettcrowson@gmail.com',
    url='https://github.com/jettdc/barb',
    long_description=ld,
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'barb = src.cli:main'
        ]
    },
    keywords='hooks git githooks automation'
)
