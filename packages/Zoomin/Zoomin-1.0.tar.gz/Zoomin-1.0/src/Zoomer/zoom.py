
from os import mkdir
from os.path import exists

import time, datetime

#####################################################################
# IMPORTANT NOTE:
# 
# Zoomin tries as hard as possible to operate in a way that is agnostic 
# to the underlying file system. It does this through the use of 
# absolute file paths wherever possible. Where this starts to break
# down is when external programs like MUSIC and Enzo are called, as
# these programs are typically run assuming they were called from
# a specific work directory. Additionally, Zoomin's unit testing
# require that config files are written out exactly the same, no
# matter what the underlying file system is. This means that certain
# assumptions have to be made about which files get written to which
# locations. When it is necessary that code is run from a 
# specific directory, the directory change will be handled by the 
# specific function that requires it. The previous working directory
# will be saved and returned to once that function has completed.
# If any functions fail to either change to the correct directory
# or change back after completion, that is considered by the 
# developer to be a bug and should be reported to:
#
#          https://github.com/cjllorente827/Zoomin/issues
#
#####################################################################

def zoom(self):
    
    start = time.time()

    while self.current_level <= self.final_level:

        print(f"""----------------------
Beginning iteration {self.current_level}
----------------------
        """)

        ########################################################################
        # Create the necessary directory structure
        ########################################################################

        # Level-specific directory
        # All outputs associated with a particular refinement level go here
        # This should be a subdirectory inside zoomin_dir
        # We should already be inside zoomin_dir at this point, since
        # zoomin_dir gets created and moved to during initialization 
        if not exists(self.level_dir):
            mkdir(self.level_dir)

        # Save the parameters we ran with to file
        # This will preserve the current_level value and allow restarting
        # between levels
        self.write_level_config()

        ########################################################################
        # Run MUSIC
        ########################################################################

        self.write_music_config()
        
        self.run_music()

        if (self.current_level == self.final_level): break # We're done!

        ########################################################################
        # Run Enzo
        ########################################################################
        self.write_enzo_config()

        self.run_enzo()

        ########################################################################
        # Find all particles in the halo we're trying to zoom in on
        ########################################################################

        self.run_particle_collection()

        ########################################################################
        # Move on to the next level
        ########################################################################
        self.set_level(self.current_level+1)
    # end while
    

    if self.run_test:
        print(f"    {self.tests_passed}/{self.tests_run} tests passed. ")

    elapsed = datetime.timedelta(seconds = time.time() - start)

    print(f"Initial conditions generated for halo {self.halo_id} after {elapsed}")


