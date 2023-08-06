from setuptools import setup, find_packages

VERSION = '0.1.0' 
DESCRIPTION = 'Clinical Notes Python Package'
LONG_DESCRIPTION = 'Pacakge to parse properly clinical text from a csv file'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="RLuligoClinicalParsing", 
        version=VERSION,
        author="Rolando Ramirez Luligo",
        author_email="rolando.luligo@tempus.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['pandas', 'regex'], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        #https://gist.github.com/nazrulworld/3800c84e28dc464b2b30cec8bc1287fc
        keywords=['Notes', 'Clinical'],
        classifiers= [
            "Development Status :: 4 - Beta",
            "Intended Audience :: Healthcare Industry",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)