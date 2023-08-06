import configparser
from setuptools import setup, find_packages

setup(
    name='Zoomin',
    description="Automated generator of initial conditions for zoom-in cosmological simulations",
    version='1.0',
    license='GNU GPL 3.0',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12"
    ],
    
    author="CJ Llorente",
    python_requires='>=3',
    package_data={
        'scripts': [
            'scripts/submit_enzo_job.sb',
            'scripts/submit_music_job.sb',
            'scripts/submit_particle_job.sb'
        ]
    },

    author_email='llorente@msu.edu',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/cjllorente827/Zoomin',
    keywords='cosmology simulation zoom',
    install_requires=[
          'numpy',
          'h5py',
          'mpi4py',
          'configparser',
          'shutil',
          'matplotlib'
      ],

)