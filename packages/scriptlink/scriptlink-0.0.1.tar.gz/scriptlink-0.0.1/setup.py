from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'scriptlink'
LONG_DESCRIPTION = 'a simple interface to a set of c++ functions for manipulating screen images and simulating input'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="scriptlink", 
        version=VERSION,
        author="Lopht",
        author_email="<bobjozeg@yahoo.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=["numpy","cv2"],
        
        keywords=['python', 'scriptlink'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: Microsoft :: Windows",
        ]
)