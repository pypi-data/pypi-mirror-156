from setuptools import setup, find_packages

VERSION = '1.0' 
DESCRIPTION = 'RA and Dec Conversion and Plotter package'
LONG_DESCRIPTION="Use this package to make converting Right Ascension and Declination values to degrees(from HMS and DMS) way easier. Simply use InNCon.Convert(...) to convert the parameters into degrees. This package also has a plotting function CelSphere.Plot() to plot the RA and Declination values on the Celestial Sphere, complete with the representation of the Equatorial Plane and vector marking the Vernal Equinox."
# Setting up
setup(
        name="CelestPlotter", 
        version=VERSION,
        author="Aditi Das",
        author_email="<aditi.das1601@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['numpy','matplotlib','astropy']
        
)