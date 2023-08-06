import configparser as cfg
from sys import exit
from os.path import abspath, exists
from os import mkdir, chdir
import numpy as np

class Zoomer():

    from .validateConfig import validateConfig
    from .load_halo_catalog import load_halo_catalog
    from .zoom import zoom
    from .run import (
        run_enzo,
        run_music,
        run_particle_collection
    )
    from .write_music_config import write_music_config
    from .write_enzo_config import write_enzo_config
    from .write_level_config import write_level_config
    from .collect_halo_particles import (
        collect_halo_particles,
        collect_halo_particles_parallel,
        get_domain_shift
    )
    from .show_particles import show_particles
    from .unit_tests import (
        test_not_implemented,
        test_load_halo_catalog,
        test_music_config_matches_solution,
        test_enzo_config_matches_solution,
        test_region_point_file_creation,
        test_run_music,
        fake_music_run,
        test_run_enzo,
        fake_enzo_run,
        fake_particle_run
    )

    def __init__(self, cfg_file):

        self.cfg_filepath = abspath(cfg_file)        

        # This is simply a record of what exists in the config file
        # and is not meant to be used for any program logic other
        # than validation/debugging 
        #
        # The values saved in the following class variables are scrubbed
        # and validated and should be considered safe to use, whereas
        # these represent the raw input from the configuration file, and
        # therefore are somewhat riskier to use.
        self.config = cfg.ConfigParser(allow_no_value=True)

        # prevents configparser from lowercasing everything
        self.config.optionxform = str
        self.config.read(self.cfg_filepath)

        # This is so Zoomin can internally keep track of its various
        # path names & values so it can easily write them out in between
        # levels
        self.keys_to_paths = {
            "zoomin_dir" : "ZoominSettings",
            "particle_sub": "ZoominSettings",
            "halo_catalog_file": "ZoominSettings",
            "music_sub": "MusicSettings",
            "transfer_function_data_file": "MusicSettings",
            "music_conf_base": "MusicSettings",
            "enzo_par_base" : "EnzoSettings",
            "enzo_sub" : "EnzoSettings",
            "grackle_data_file" : "EnzoSettings",
        }


        # Set all parameter values
        self.zoomin_dir = abspath(self.config["ZoominSettings"]["zoomin_dir"])
        self.simulation_name = self.config["ZoominSettings"]["simulation_name"]
        self.box_length = self.config.getfloat("ZoominSettings", "box_length")
        self.halo_catalog_file = abspath(self.config["ZoominSettings"]["halo_catalog_file"])
        self.sub_cmd = self.config["ZoominSettings"]["sub_cmd"]
        self.dry_run = self.config.getboolean("ZoominSettings", "dry_run")
        self.run_test = self.config.getboolean("ZoominSettings", "run_test")
        self.level_suffix = self.config["ZoominSettings"]["level_suffix"]
        self.halo_id = self.config.getint("ZoominSettings", "halo_id")
        self.final_level = self.config.getint("ZoominSettings", "final_level")
        self.initial_level = self.config.getint("ZoominSettings", "initial_level")
        self.particle_sub = abspath(self.config["ZoominSettings"]["particle_sub"])

        self.music_conf_base = abspath(self.config["MusicSettings"]["music_conf_base"])
        self.music_sub = abspath(self.config["MusicSettings"]["music_sub"])
        self.music_run_finished = self.config["MusicSettings"]["music_run_finished"]
        self.transfer_function_data_file = abspath(self.config["MusicSettings"]["transfer_function_data_file"])

        self.enzo_par_base = abspath(self.config["EnzoSettings"]["enzo_par_base"])
        self.enzo_sub = abspath(self.config["EnzoSettings"]["enzo_sub"])
        self.enzo_run_finished = self.config["EnzoSettings"]["enzo_run_finished"]
        self.grackle_data_file = abspath(self.config["EnzoSettings"]["grackle_data_file"])

        self.last_enzo_out = self.config["EnzoSettings"]["last_enzo_out"]
        self.first_enzo_out = self.config["EnzoSettings"]["first_enzo_out"]

        self.validateConfig()

        self.current_level = 0
        self.level_dir = ""
        self.music_conf_name = ""
        self.music_log_file = ""
        self.enzo_conf_name = ""
        self.initial_particle_file = ""
        self.final_particle_file = ""
        self.refine_particles_file = ""

        # MUSIC shifts the entire box during a zoom-in run so that the 
        # region of interest is close to the center of the box
        # This saves the un-normalized shift at each level, 
        # i.e. the shift that MUSIC uses and understands
        #
        # To translate these shifts to box coordinates, you must 
        # divide the values by the number of root grid cells
        #
        # E.g.
        # If your box is 32x32x32 (levelmin = 5 in the MUSIC config)
        # then divide the values by 32
        # Zoomin derives this number from the levelmin stat in the MUSIC config
        #
        # NB: the first value added to this should always be (0,0,0)
        self.box_shift = [np.zeros(3)] * (self.final_level+1)

        self.set_level(self.initial_level)

        self.tests_run = 0
        self.tests_passed = 0
        
        # dictionary of halos, keyed by their halo id
        halo_catalog = self.load_halo_catalog()

        # HaloData object, defined in HaloData.py
        # TODO: create a deep copy of this so the 
        #       halo catalog can be garbage collected
        self.target_halo = halo_catalog[self.halo_id]

        if (self.run_test):
            self.test_load_halo_catalog()

        # Base directory where all outputs will go
        if not exists(self.zoomin_dir):
            mkdir(self.zoomin_dir)
        
        # make sure we're in the working directory
        chdir(self.zoomin_dir)

        print(f"""
Running Zoomin with the following parameters: 

Halo ID: {self.halo_id}
Final refine Level: { self.final_level}
Initial refine level: {self.initial_level}

Zoomin config : {self.cfg_filepath}
""")

    # end __init__


    ########################################################################
    # This function manages zoomin's current state by keeping track
    # of which directories and files we need to be modifying at any given time
    ####################################################################
    # Definitions for all these values
    # 
    # Quick terminology clarification
    # a "filename" is just that, an unqualified file name with no path information
    # an "absolute path" is the fully qualified path to a particular file or directory
    # a "relative path" is relative to the value of zoomin_dir
    #
    # current_level - Current iteration, typically an integer from 0-4
    # zoomin_dir - absolute path to the directory that stores all 
    #              files relevant to a particular simulation
    # level_dir - absolute path to the directory that stores all files
    #           relevant to a particular level iteration
    # test_solutions_dir - absolute path to solutions for unit tests for a 
    #                      particular refinement level
    # music_conf_name - music config filename for a particular level 
    # enzo_conf_name - enzo config filename for a particular level 
    # initial_particle_file - absolute path to file where initial particle positions are stored
    # final_particle_file - absolute path to file where final particle positions are stored
    # region_point_file - absolute path to file MUSIC reads in to create refine region
    ########################################################################
    def set_level(self, level):
        self.current_level = level
        self.level_suffix = f"{self.level_suffix[:-1]}{self.current_level}"
        self.level_dir = f"{self.zoomin_dir}/{self.simulation_name}{self.level_suffix}"
        self.test_solutions_dir = f"{self.zoomin_dir}/solutions/{self.simulation_name}{self.level_suffix}"
        self.level_conf_name = f"{self.simulation_name}{self.level_suffix}.zoom"
        self.music_conf_name = f"{self.simulation_name}{self.level_suffix}.conf"
        self.music_log_file = f"{self.level_dir}/{self.simulation_name}{self.level_suffix}.conf_log.txt"
        self.enzo_conf_name = f"{self.simulation_name}{self.level_suffix}.enzo"
        self.initial_particle_file = f"{self.level_dir}/halo_{self.halo_id}_particles_initial"
        self.final_particle_file = f"{self.level_dir}/halo_{self.halo_id}_particles_final"
        self.region_point_file = f"{self.level_dir}/halo_{self.halo_id}_region_point_file{self.level_suffix}"
    # end set_level

    ########################################################################
    # Convenience functions for reading configuration files at 
    # different levels 
    ######################################################################## 
    def get_level_config(self, level=None):

        if level is None:
            return self.cfg_filepath

        # If the level argument was not given, return the base config
        config_fname = self.level_conf_name
        
        prev_level = self.current_level
        self.set_level(level)
        config_fname = f"{self.level_dir}/{self.level_conf_name}"

        # read in the file
        level_conf = cfg.ConfigParser()
        # prevents configparser from lowercasing everything
        level_conf.optionxform = str
        level_conf.read(config_fname)

        # reset our level if necessary
        if level is not None:
            self.set_level(prev_level)

        # return the parsed file object
        return level_conf

    def get_music_config(self, level=None):

        # If the level argument was not given, return the base config
        config_fname = self.music_conf_base
        
        # If the level argument was given, save the current level
        # and set us to the level given by the argument
        if level is not None:
            prev_level = self.current_level
            self.set_level(level)
            config_fname = f"{self.level_dir}/{self.music_conf_name}"

        # read in the file
        music_conf = cfg.ConfigParser()
        # prevents configparser from lowercasing everything
        music_conf.optionxform = str
        music_conf.read(config_fname)

        # reset our level if necessary
        if level is not None:
            self.set_level(prev_level)

        # return the parsed file object
        return music_conf

    def get_enzo_config(self, level=None):

        # If the level argument was not given, return the base config
        config_fname = self.enzo_par_base
        
        # If the level argument was given, save the current level
        # and set us to the level given by the argument
        if level is not None:
            prev_level = self.current_level
            self.set_level(level)
            config_fname = f"{self.level_dir}/{self.enzo_conf_name}"

        # read in the file
        enzo_conf = cfg.ConfigParser()
        # prevents configparser from lowercasing everything
        enzo_conf.optionxform = str
        
        # prepend a dummy section so configparser will work =P
        with open(config_fname) as stream:
            enzo_conf.read_string("[top]\n" + stream.read())  

        # reset our level if necessary
        if level is not None:
            self.set_level(prev_level)

        # return the parsed file object
        return enzo_conf

    def get_region_point_filepath(self, level=None):

        # If the level argument was not given, return the current filepath
        filepath = self.region_point_file
        
        # If the level argument was given, save the current level
        # and set us to the level given by the argument
        if level is not None:
            prev_level = self.current_level
            self.set_level(level)

            # TODO: ensure this copies by value, not by reference
            filepath = self.region_point_file

            # reset our level if necessary
            self.set_level(prev_level)

        # return the filepath
        return filepath

# end class