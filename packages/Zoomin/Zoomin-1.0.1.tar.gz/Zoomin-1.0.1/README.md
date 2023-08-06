# Zoomin

Automated pipeline for the creation of initial conditions for zoom-in simulations with MUSIC and Enzo.

Documentation is currently a work in progress. Basic information has been supplied as a general outline, but more specific information will be added in future to facilitate running and troubleshooting. Sections that are understood by the author to be underdeveloped will be marked with a (WIP) in their section headers. 

# How it works

Start by running Enzo as normal with the desired cosmological volume. Find a halo within that simulation at the desired reshift using FOF, HOP, or Rockstar. You can either include the halo location and radius in the zoom config file, or specify a path to a halo catalog file and halo id. 

Zoomin will then run a unigrid simulation with only dark matter particles and 
determine which of those particles end up in the halo by the desired redshift. 

Those particles' positions will then be fed back into MUSIC so that the area they occupy can be refined one level higher than the unigrid. The simulation will then
be rerun with a refine region around those particles. 

This repeats for a user-specified number of iterations with the last set of 
initial conditions being created with baryons turned back on. This last set 
of initial conditions is suitable for use in a zoom-in simulation. 

# Setup (WIP)

- Install MUSIC

- Install Enzo

- Install Rockstar

- Run pre-flight simulation

- Find interesting halo

- Supply halo and directory information in zoomin config file

- Supply MUSIC and Enzo base config files, along with other miscellaneous files
requires to run them. 

- Modify submission scripts in `scripts` folder to work with your computer system (example scripts have been given for SLURM and PBS). 

- Run with :   `zoomin yourconfigfile.zoom`






