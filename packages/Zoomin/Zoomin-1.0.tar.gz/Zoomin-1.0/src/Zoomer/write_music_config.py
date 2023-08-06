import configparser as cfg
from os.path import basename, exists, abspath
from shutil import copyfile
from sys import exit

def write_music_config(self):

    if self.current_level == 0:
        create_from_base(self)
    elif self.current_level <= self.final_level:
        create_from_last_iteration(self)
    else : # some kind of error has occurred
        print("Error: Current level ({self.current_level}) is above final level ({self.final_level}). Exiting.")
        exit()

    # run unit tests
    if self.run_test:
        self.test_music_config_matches_solution()


def create_from_last_iteration(self):
    music_conf = self.get_music_config(level=self.current_level-1)

    # copy the given transfer function file to the run directory
    transfer_src = self.transfer_function_data_file
    transfer_dst = f"{self.level_dir}/{basename(transfer_src)}"
    copyfile(transfer_src, transfer_dst)

    # copy the region point file from the last iteration into the new directory
    region_point_src = self.get_region_point_filepath(level=self.current_level-1)
    region_point_dst = f"{self.level_dir}/{basename(region_point_src)}"
    copyfile(region_point_src, region_point_dst)

    levelmin = music_conf.getint("setup","levelmin")
    levelmax = music_conf.getint("setup","levelmax")

    music_conf["setup"]["region"] = "convex_hull"
    music_conf["setup"]["levelmin_TF"] = str(levelmax + 1)
    music_conf["setup"]["levelmax"] = str(levelmax + 1)
    music_conf["setup"]["region_point_file"] = basename(region_point_dst)

    # If we're on the last iteration, add baryons to the ICs
    if self.current_level == self.final_level:
        music_conf["setup"]["baryons"] = "yes"

    # MUSIC requires the box shift be added to the config file if running 
    # from the results of a previously zoomed in simulation
    if self.current_level > 1:
        x = int(self.box_shift[self.current_level-1][0])
        y = int(self.box_shift[self.current_level-1][1])
        z = int(self.box_shift[self.current_level-1][2])
        region_point_shift = "{0:d},{1:d},{2:d}".format(x,y,z)
        music_conf["setup"]["region_point_shift"] = region_point_shift
        music_conf["setup"]["region_point_levelmin"] = str(levelmin)


    # write out the new music config file
    music_conf_fname = f"{self.level_dir}/{self.music_conf_name}"
    with open(music_conf_fname, 'w') as new_music_conf:
        music_conf.write(new_music_conf)

    print(f"Created new MUSIC config at {music_conf_fname}")


def create_from_base(self):
    music_conf = self.get_music_config()

    transfer_src = self.transfer_function_data_file
    transfer_dst = f"{self.level_dir}/{basename(self.transfer_function_data_file)}"
    
    # copy the given transfer function file to the run directory
    copyfile(transfer_src, transfer_dst)

    # add the file to the music config
    music_conf["cosmology"]["transfer_file"] = basename(transfer_dst)

    ic_dir = f"{self.level_dir}/IC"
    music_conf["output"]["filename"] = basename(ic_dir)

    # write out the new music config file
    music_conf_fname = f"{self.level_dir}/{self.music_conf_name}"
    with open(music_conf_fname, 'w') as new_music_conf:
        music_conf.write(new_music_conf)

    print(f"Created new MUSIC config at {music_conf_fname}")

