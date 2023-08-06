
import numpy as np
import h5py, re, os
import sys

def collect_halo_particles(self):

    ##############################################################
    # Scan last enzo output directory for all .cpuXXXX files
    ##############################################################

    final_out_files = get_simulation_outputs(self.level_dir, self.last_enzo_out)

    initial_out_files = get_simulation_outputs(self.level_dir, self.first_enzo_out)

    ##############################################################
    # Go through each file and 
    # save all particles that reside inside our halo
    ##############################################################

    halo_center = np.array([
        self.target_halo.X,
        self.target_halo.Y,
        self.target_halo.Z
    ])

    # Get the domain shift from the MUSIC log file
    self.get_domain_shift()

    # Grab the base music config
    music_base_conf = self.get_music_config()

    # read in the minimum refinement level
    # this is the power of 2 that sets the root grid refinement
    music_level_min = music_base_conf.getint("setup", "levelmin")

    # translate the shift into box coordinates
    shift = self.box_shift[self.current_level] / (2**music_level_min)

    # apply the shift
    halo_center += shift
    print(f"Halo center shifted by {shift} ({self.box_length*shift} Mpc)")

    print(f"""Searching for particles within halo {self.halo_id}
with position {halo_center} ({halo_center*self.box_length} Mpc)
and radius {self.target_halo.Rvir} ({1000*self.target_halo.Rvir*self.box_length} kpc)""")

    particle_final_positions = collect_particles(final_out_files, 
        halo_center=halo_center,
        halo_rad=self.target_halo.Rvir)

    if len(particle_final_positions) == 0:
        print(f"""Error: No particles found in halo {self.halo_id}.\nExiting""")
        sys.exit()
    # end if

    particle_initial_positions = collect_particles(initial_out_files, 
        indexes=list(particle_final_positions[:,0]))

    header = "id X Y Z"
    number_format = [
        '%d',
        '%.18f',
        '%.18f',
        '%.18f'
    ]

    # These two files save particle positions along with ids
    # and are used mostly for debugging and data inspection
    np.savetxt(self.final_particle_file, 
        particle_final_positions, 
        header=header,
        fmt=number_format)

    np.savetxt(self.initial_particle_file, 
        particle_initial_positions, 
        header=header,
        fmt=number_format)

    # This file saves the points that get used as the region definition
    # for MUSIC
    np.savetxt(self.region_point_file, 
        particle_initial_positions[:,1:], 
        fmt=number_format[1:])

    print(f"Particle positions saved to {self.region_point_file}")

    if self.run_test:
        self.test_region_point_file_creation()
# end collect_halo_particles

def collect_halo_particles_parallel(self, comm):

    size = comm.Get_size()
    rank = comm.Get_rank()

    # begin serial section
    if (rank == 0):

        ##############################################################
        # Scan last enzo output directory for all .cpuXXXX files
        ##############################################################

        final_out_files = get_simulation_outputs(self.level_dir, self.last_enzo_out)

        scatter_final = [[] for i in range(size)]

        cycle = 0
        for f in final_out_files:
            scatter_final[cycle] += [f]
            cycle = cycle+1 if cycle < size-1 else 0


        initial_out_files = get_simulation_outputs(self.level_dir, self.first_enzo_out)

        scatter_initial = [[] for i in range(size)]

        cycle = 0
        for f in initial_out_files:
            scatter_initial[cycle] += [f]
            cycle = cycle+1 if cycle < size-1 else 0

        ##############################################################
        # Go through each file and 
        # save all particles that reside inside our halo
        ##############################################################

        halo_center = np.array([
            self.target_halo.X,
            self.target_halo.Y,
            self.target_halo.Z
        ])

        # Get the domain shift from the MUSIC log file
        self.get_domain_shift()

        # Grab the base music config
        music_base_conf = self.get_music_config()

        # read in the minimum refinement level
        # this is the power of 2 that sets the root grid refinement
        music_level_min = music_base_conf.getint("setup", "levelmin")

        # translate the shift into box coordinates
        shift = self.box_shift[self.current_level] / (2**music_level_min)

        # apply the shift
        halo_center += shift
        print(f"Halo center shifted by {shift} ({self.box_length*shift} Mpc)")

        print(f"""Searching for particles within halo {self.halo_id}
    with position {halo_center} ({halo_center*self.box_length} Mpc)
    and radius {self.target_halo.Rvir} ({1000*self.target_halo.Rvir*self.box_length} kpc)""")
    else:
        final_out_files = None
        initial_out_files = None
        scatter_final = None
        scatter_initial = None
        halo_center = None
    # end serial section

    # begin parallel section

    ##############################################################
    # Broadcast halo center and scatter file names across
    # processes
    ##############################################################

    halo_center = comm.bcast(halo_center, root=0)
    final_out_files = comm.scatter(scatter_final, root=0)
    initial_out_files = comm.scatter(scatter_initial, root=0)

    print(f"Rank {rank} working on {initial_out_files}")

    gather_final_positions = collect_particles(final_out_files, 
        halo_center=halo_center,
        halo_rad=self.target_halo.Rvir)

    ##############################################################
    # Gather final positions onto the root process
    ##############################################################
    gather_final_positions = comm.gather(gather_final_positions, root=0)

    # flatten the result
    particle_final_positions = None
    if rank == 0:
        for i in range(size):
            if gather_final_positions[i].size == 0:
                continue
            if particle_final_positions is None:
                particle_final_positions = np.copy(gather_final_positions[i])
            else:
                particle_final_positions = np.append(particle_final_positions, gather_final_positions[i], axis=0)

        

    ##############################################################
    # Broadcast the particle ids to all processes
    ##############################################################
    particle_final_positions = comm.bcast(particle_final_positions, root=0)

    gather_initial_positions = collect_particles(initial_out_files, 
        indexes=list(particle_final_positions[:,0]))

    ##############################################################
    # Gather initial positions onto the root process
    ##############################################################
    gather_initial_positions = comm.gather(gather_initial_positions, root=0)

    # flatten the result
    particle_initial_positions = None
    if rank == 0:
        for i in range(size):
            if gather_initial_positions[i].size == 0:
                continue
            if particle_initial_positions is None:
                particle_initial_positions = np.copy(gather_initial_positions[i])
            else:
                particle_initial_positions = np.append(particle_initial_positions, gather_initial_positions[i], axis=0)

    # end parallel section

    # begin serial section
    if (rank == 0):
        header = "id X Y Z"
        number_format = [
            '%d',
            '%.18f',
            '%.18f',
            '%.18f'
        ]
        # These two files save particle positions along with ids
        # and are used mostly for debugging and data inspection
        np.savetxt(self.final_particle_file, 
            particle_final_positions, 
            header=header,
            fmt=number_format)

        np.savetxt(self.initial_particle_file, 
            particle_initial_positions, 
            header=header,
            fmt=number_format)

        # This file saves the points that get used as the region definition
        # for MUSIC
        np.savetxt(self.region_point_file, 
            particle_initial_positions[:,1:], 
            fmt=number_format[1:])

        print(f"Particle positions saved to {self.region_point_file}")

        if self.run_test:
            self.test_region_point_file_creation()

    # end serial section

# end collect_halo_particles_parallel

##############################################################
# Scans through a list of hdf5 files to find all particles
# that either share an index with the list of indexes
# - or -
# lie within the sphere specified by the halo center and radius
# if indexes is None, then halo_center and halo_rad must be 
# given. Defaults to using indexes if all 3 are given
#
# This function will always ignore star particles and active particles
##############################################################
def collect_particles(filenames, 
    indexes=None, 
    halo_center=None, 
    halo_rad=None):


    # Validate the arguments passed in
    valid_indexes = indexes is not None and len(indexes) > 0
    valid_halo_center = halo_center is not None and len(halo_center) == 3
    valid_halo_rad = halo_center is not None
    
    # If we were passed a lsit of indexes, use those to find the particles
    # Else use the halo center and radius to find particles
    if not valid_indexes:
        if not valid_halo_center or not valid_halo_rad:
            raise ValueError("halo_center and halo_rad cannot be None if indexes is None")
        find_in_halo = True
    else:
        find_in_halo = False


    particles = []

    for filename in filenames:
    
        with h5py.File(filename, 'r') as f:

            print(f"Reading in {filename}")

            grids = list(f.keys())
            grids.remove('Metadata')
            
            for grid in grids:
                print(f"Scanning {grid}")

                for i, particle_type in enumerate(f[grid]["particle_type"]):

                    if particle_type != 1: # dark matter particles only
                        continue

                    particle_index = int(f[grid]["particle_index"][i])
                    r = [
                        f[grid]["particle_position_x"][i],
                        f[grid]["particle_position_y"][i],
                        f[grid]["particle_position_z"][i]
                    ]

                    if find_in_halo and np.linalg.norm(r - halo_center) <= halo_rad:
                        
                        # *r unpacks r  
                        # i.e. the equivalent of writing "r[0],r[1],r[2]"
                        particle_entry = np.array([particle_index, *r])
                        particles.append(particle_entry)

                    elif not find_in_halo and particle_index in indexes:
                        indexes.remove(particle_index) # remove any found indexes to speed up search a bit
                        particle_entry = np.array([particle_index, *r])
                        particles.append(particle_entry)
            # end for grid
        # end with
    # for filename

    return np.array(particles)


def get_simulation_outputs(simulation_dir, output_name):

    pattern = re.compile(f'{output_name}.cpu[0-9][0-9][0-9][0-9]')

    all_files =  os.listdir( os.path.join(simulation_dir, output_name) )

    matched_files = []

    for f in all_files:
        match  = pattern.match(f)
        if match != None:
            fname = match.group()
            full_path = os.path.join(simulation_dir, output_name, fname)
            matched_files.append(full_path)

    return matched_files

def get_domain_shift(self):

    pattern = re.compile("Domain shifted by")

    domain_shift_text = ""

    print(f"Reading from {self.music_log_file}")
    with open(self.music_log_file) as f:
        lines = f.readlines()
        for line in lines:
            match = pattern.search(line)
            if match is not None:
                domain_shift_text = line
                break
        # end for
    # end with

    first_paren = domain_shift_text.index('(')+1
    second_paren = domain_shift_text.index(')')

    shift_strings = domain_shift_text[first_paren:second_paren].split(',')

    shift = np.zeros(3)
    for i in range(3):
        shift[i] = int(shift_strings[i].strip())

    self.box_shift[self.current_level] = shift

    return shift