from os.path import exists

valid_keys = [
    "zoomin_dir",
    "simulation_name",
    "halo_id",
    "initial_level",
    "final_level",
    "box_length",
    "particle_sub",
    "music_conf_base",
    "music_exe",
    "music_sub",
    "music_run_finished",
    "enzo_par_base",
    "enzo_exe",
    "enzo_sub",
    "enzo_run_finished",
    "last_enzo_out",
    "first_enzo_out",
    "halo_catalog_file",
    "sub_cmd",
    "run_test",
    "level_suffix",
    "grackle_data_file",
    "transfer_function_data_file",
    "dry_run"
]

def validateConfig(self):

    if self.sub_cmd is None or self.sub_cmd == "None" or self.sub_cmd == "":
        raise ValueError("sub_cmd argument must be set")

    for section, params in self.config.items():
        for key, value in params.items():
            if key not in valid_keys:
                print(f"[Warning]: {key} not in list of valid keys and will not be used.")
            #end if
        #end for
    #end for
    
    for key in self.keys_to_paths.keys():
        filename = getattr(self, key)
        try:
            assert( exists(filename) )
        except AssertionError as e:
            raise FileNotFoundError(f'"Error: {key} = {filename}" supplied in {self.cfg_filepath} but no such path exists')
        # end try
    # end for key
    
    
