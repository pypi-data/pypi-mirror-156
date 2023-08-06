import configparser as cfg
from os.path import basename, exists, abspath
from shutil import copyfile
from sys import exit

def write_level_config(self):
    
    # change the initial level to our current level
    self.config["ZoominSettings"]["initial_level"] = str(self.current_level)

    # processes run from these should not run tests
    self.config["ZoominSettings"]["run_test"] = "False"

    #TODO: but maybe they should do dry runs?
    self.config["ZoominSettings"]["dry_run"] = "False"

    # make sure that these values are set to the full path
    for key, section in self.keys_to_paths.items():
        filepath = getattr(self, key)
        self.config[section][key] = filepath


    level_conf_fname = f"{self.level_dir}/{self.level_conf_name}"
    with open(level_conf_fname, 'w') as new_level_conf:
        self.config.write(new_level_conf)





