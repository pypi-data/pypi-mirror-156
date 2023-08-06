from setuptools import setup

setup(
    name='holtz-tools',
    version='0.3.2',    
    description='Python utility tools',
    url='https://github.com/holtzmanjon/tools',
    author='Jon Holtzman',
    author_email='holtz@nmsu.edu',
    license='MIT',
    packages=['tools'],
    package_dir={"": "python"},
    install_requires=[
                      'numpy',                     
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)

