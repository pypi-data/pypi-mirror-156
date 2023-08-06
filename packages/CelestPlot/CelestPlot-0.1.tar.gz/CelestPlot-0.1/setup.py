from setuptools import setup, find_packages

VERSION = '0.1' 
DESCRIPTION = 'RA and Dec Conversion package'

# Setting up
setup(
        name="CelestPlot", 
        version=VERSION,
        author="Aditi Das",
        author_email="<aditi.das1601@gmail.com>",
        description=DESCRIPTION,
        packages=find_packages(),
        install_requires=['numpy','matplotlib','astropy']
        
)