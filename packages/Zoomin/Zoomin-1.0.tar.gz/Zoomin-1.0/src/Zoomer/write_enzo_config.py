from configparser import ConfigParser

def write_enzo_config(self):

    enzo_base = self.get_enzo_config()

    ##################################################################
    # read in the parameter file MUSIC creates and copy those over 
    # onto the enzo base file
    ##################################################################

    MUSIC_params = ConfigParser()
    # prevents configparser from lowercasing everything
    MUSIC_params.optionxform = str

    # prepend a dummy section so configparser will work =P
    with open(f"{self.level_dir}/parameter_file.txt") as stream:
        MUSIC_params.read_string("[top]\n" + stream.read())


    # overwrite the base parameter values
    for section, params in MUSIC_params.items():
        for key in params.keys():
            # Stop MUSIC from controlling the final redshift
            if key == "CosmologyFinalRedshift": continue
            enzo_base[section][key] = MUSIC_params[section][key]
        #end for
    #end for

    # set the refinement level
    refine_level = enzo_base.getint("top", "MaximumRefinementLevel") + self.current_level
    enzo_base[section]["MaximumRefinementLevel"] = str(refine_level)

    # TODO: This is where shit is gonna get fucked up
    #
    # Ok so, this parameter can potentially be a list of floats,
    # meaning that proper treatment of its value should be 
    # split on white space, and cast to a list of floats
    #
    # The specific index that needs to be changed is the index
    # that corresponds to where a 4 appears in the CellFlaggingMethod
    # parameter.
    #
    # 4 in CellFlaggingMethod refers to the dark matter particle refinement
    # and thats the value we're trying to target with this
    #
    # So a proper treatment of this parameter is as follows:
    #
    # Read in CellFlaggingMethod
    # Split on whitespace, cast to ints
    # Find the index of that list that contains the value 4
    # Read in MinimumOverDensityForRefinement
    # Split on whitespace, cast to floats
    # set modfr to the value located at the index with value 4
    # Create a new list of floats the same size as CellFlaggingMethod's list
    # Insert modfr / (8**current_level) at index
    # set all other values to what they were in the base parameter file
    # cast the list to a string of whitespace-delimited float values
    # set MinimumOverDensityForRefinement to that string
    #
    # thats the only way I can think of to not fuck this up
    modfr = enzo_base.getfloat("top", "MinimumOverDensityForRefinement")
    enzo_base[section]["MinimumOverDensityForRefinement"] = str(modfr / (8**self.current_level))

    # write out the new enzo config file
    enzo_conf_fname = f"{self.level_dir}/{self.enzo_conf_name}"
    with open(enzo_conf_fname, 'w') as new_enzo_conf:
        enzo_base.write(new_enzo_conf)

    print(f"Created new Enzo config at {enzo_conf_fname}")

    # run unit tests
    if self.run_test:
        self.test_enzo_config_matches_solution()