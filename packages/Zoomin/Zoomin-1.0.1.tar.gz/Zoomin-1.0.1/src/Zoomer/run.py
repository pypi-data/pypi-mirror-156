import os, subprocess, time
from shutil import copytree
from os.path import exists

env_flag = {
    "qsub" : "-v",
    "sbatch" : "--export="
}

def run_music(self):
    # save the current directory
    prev_dir = os.getcwd()
    # move us into the work directory
    os.chdir(self.level_dir)

    # Handle the dry run
    if self.dry_run:
        self.fake_music_run()
        self.test_run_music()
        return 

    # If previous run results exist, then use those
    ic_dir = f"{self.level_dir}/IC"
    if exists(ic_dir):
        print("Found results of previous MUSIC run.")
        # Copy the results one level up
        copytree(ic_dir, self.level_dir,dirs_exist_ok=True)
        # Get the domain shift from the MUSIC log file
        self.get_domain_shift()
        if self.run_test: self.test_run_music()
        return

    # figure out which file we look for to see if MUSIC is finished running
    if self.current_level > 0:
        run_finished_file = f"{ic_dir}/{self.music_run_finished}.{self.current_level}"
    else:
        run_finished_file = f"{ic_dir}/{self.music_run_finished}"
        
    
    # set environment variables
    env_var = f"WORKING_DIR={self.level_dir},MUSIC_CONF_FILE={self.music_conf_name}"
    
    # put together the submission command
    cmd = f"{self.sub_cmd} {env_flag[self.sub_cmd]}{env_var} {self.music_sub}"
    print(f"Running MUSIC with:\n{cmd}")

    # submit the job
    proc = subprocess.run(cmd, 
        shell=True, text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)

    print(proc.stdout)

    print(f"Waiting for {run_finished_file}...")

    # wait for the job to finish
    while( not os.access(run_finished_file, os.W_OK) ):
        time.sleep(3)
    
    # Copy the results one level up
    copytree(ic_dir, self.level_dir,dirs_exist_ok=True)

    # Get the domain shift from the MUSIC log file
    self.get_domain_shift()

    # run unit tests
    if self.run_test:
        self.test_run_music()
    # move us into the previous directory
    os.chdir(prev_dir)

def run_enzo(self):
    # save the current directory
    prev_dir = os.getcwd()
    # move us into the work directory
    os.chdir(self.level_dir)

    if self.dry_run:
        self.fake_enzo_run()
        self.test_run_enzo()
        return 
    # end if dry run

    # If previous run results exist, then use those
    if os.access(self.enzo_run_finished, os.W_OK):
        print("Found results of previous Enzo run.")
        if self.run_test: self.test_run_enzo()
        return

    env_var = f"WORKING_DIR={self.level_dir},ENZO_PAR_FILE={self.enzo_conf_name}"

    cmd = f"{self.sub_cmd} {env_flag[self.sub_cmd]}{env_var} {self.enzo_sub}"

    print(f"Running Enzo with:\n{cmd}")

    proc = subprocess.run(cmd, 
        shell=True, text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)

    print(proc.stdout)

    print(f"Waiting for {self.enzo_run_finished}...")

    while( not os.access(self.enzo_run_finished, os.W_OK) ):
        time.sleep(3)

    print(f"Found {self.enzo_run_finished}. Continuing.")

    if self.run_test:
        self.test_run_enzo()
    # move us into the previous directory
    os.chdir(prev_dir)

def run_particle_collection(self):
    # save the current directory
    prev_dir = os.getcwd()
    # move us into the work directory
    os.chdir(self.level_dir)

    if self.dry_run:
        self.fake_particle_run
        self.test_region_point_file_creation()
        return
    # end if dry run

    # If previous run results exist, then use those
    if os.access(self.region_point_file, os.W_OK):
        print("Found results of previous particle collection run.")
        if self.run_test: self.test_region_point_file_creation()
        return

    env_var = f"WORKING_DIR={self.level_dir},ZOOMIN_CONF_FILE={self.level_conf_name}"

    cmd = f"{self.sub_cmd} {env_flag[self.sub_cmd]}{env_var} {self.particle_sub}"

    print(f"Running particle collection with:\n{cmd}")

    proc = subprocess.run(cmd, 
        shell=True, text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)

    print(proc.stdout)

    print(f"Waiting for {self.region_point_file}...")

    while( not os.access(self.region_point_file, os.W_OK) ):
        time.sleep(3)

    print(f"Found {self.region_point_file}. Continuing.")

    if self.run_test:
        self.test_region_point_file_creation()
    # move us into the previous directory
    os.chdir(prev_dir)