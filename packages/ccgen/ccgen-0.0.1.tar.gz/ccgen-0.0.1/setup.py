from setuptools import setup, find_packages
import os

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='ccgen',
    packages=find_packages(),
    include_package_data=True,
    version="0.0.1",
    description='CC GENERATOR FOR BIN',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='AKXVAU',
    author_email='dev.akxvau@gmail.com',
    install_requires=['lolcat'],
    
    
    keywords=['dcbd', 'akxvau', 'dcbd04', 'noob-hacker', 'dcbd tool', 'toxicvirus21', 'gencc', 'ccgen', 'bin', 'make cc'],
    classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Operating System :: OS Independent',
            'Environment :: Console',
    ],
    
    license='MIT',
    entry_points={
            'console_scripts': [
                'ccgen = ccgen.ccgen:menu',
                
            ],
    },
    python_requires='>=3.9'
)