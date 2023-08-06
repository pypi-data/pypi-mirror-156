
import filecmp, subprocess, os
from os.path import exists, basename
from shutil import copyfile, copytree

def fail(self, msg):
    print (f"\n[Test {self.tests_run} failed] : {msg}\n")

def succeed(self, msg=None):
    if msg == None:
        print (f"\n[Test {self.tests_run} passed]\n")
    else:
        print (f"\n[Test {self.tests_run} passed] : {msg}\n")


def test_float_equality(a, b, threshold=1e-5):

    eps = abs((a-b)/a)
    return eps < threshold

def test_load_halo_catalog(self):
    self.tests_run += 1

    errors = False

    # Test solutions
    answer_key = {
        "Mvir" : 4.5257e+11,
        "Rvir" : 196.059/25000,
        "X"    : 6.01253/25, 
        "Y"    : 22.40417/25,
        "Z"    : 2.30050/25
    }

    for key, answer in answer_key.items():
        attr = getattr(self.target_halo, key)
        try :
            assert( test_float_equality(attr, answer) )
        except AssertionError as e:
            fail(self, f"{key} values {attr} and {answer} are not equal.")
            errors = True
            
    if errors : return
    
    self.tests_passed += 1
    succeed(self)

def test_music_config_matches_solution(self):
    self.tests_run += 1
    errors = False
    solution_file = f"{self.test_solutions_dir}/{self.simulation_name}{self.level_suffix}.conf"

    generated_file = f"{self.level_dir}/{self.music_conf_name}"

    original_file = self.transfer_function_data_file
    copied_file = f"{self.level_dir}/{basename(self.transfer_function_data_file)}"

    try: 
        assert(filecmp.cmp(generated_file, solution_file, shallow=False))
    except AssertionError as e:
        fail(self, f"{generated_file} does not match solution file at {solution_file}")
        errors = True
    except FileNotFoundError as e:
        fail(self, f"{e.filename} does not exist.")
        errors = True

    try: 
        assert(filecmp.cmp(copied_file, original_file, shallow=False))
    except AssertionError as e:
        fail(self, f"{copied_file} does not match original file at {original_file}")
        errors = True
    except FileNotFoundError as e:
        fail(self, f"{e.filename} does not exist.")
        errors = True

    if errors : return
    self.tests_passed += 1
    succeed(self)

def test_enzo_config_matches_solution(self):
    self.tests_run += 1
    errors = False
    solution_file = f"{self.test_solutions_dir}/{self.simulation_name}{self.level_suffix}.enzo"

    generated_file = f"{self.level_dir}/{self.enzo_conf_name}"

    try: 
        assert(filecmp.cmp(generated_file, solution_file, shallow=False))
    except AssertionError as e:
        fail(self, f"{generated_file} does not match solution file at {solution_file}")
        errors = True
    except FileNotFoundError as e:
        fail(self, f"{e.filename} does not exist.")
        errors = True

    if errors : return
    self.tests_passed += 1
    succeed(self)
    

# This list does not capture all of the MUSIC outputs,
# just the ones we care about
MUSIC_outfiles_L0 = [
    "parameter_file.txt",
    "ParticleDisplacements_x",
    "ParticleDisplacements_y",
    "ParticleDisplacements_z",
    "ParticleVelocities_x",
    "ParticleVelocities_y",
    "ParticleVelocities_z"
]

# MUSIC outputs for levels greater than 0
MUSIC_outfiles_Lgt0 = [
    "parameter_file.txt",
    "ParticleDisplacements_x.0",
    "ParticleDisplacements_y.0",
    "ParticleDisplacements_z.0",
    "ParticleVelocities_x.0",
    "ParticleVelocities_y.0",
    "ParticleVelocities_z.0",
    "ParticleDisplacements_x.1",
    "ParticleDisplacements_y.1",
    "ParticleDisplacements_z.1",
    "ParticleVelocities_x.1",
    "ParticleVelocities_y.1",
    "ParticleVelocities_z.1"
]

def fake_music_run(self):

    MUSIC_outfiles = MUSIC_outfiles_L0 if self.current_level == 0 else MUSIC_outfiles_Lgt0

    for fname in MUSIC_outfiles:
        cp_cmd = f"cp {self.test_solutions_dir}/{fname} {self.level_dir}/."
        proc = subprocess.run(cp_cmd, 
            shell=True, text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

        if len(proc.stdout) > 0:
            print(proc.stdout)

def test_run_music(self):

    self.tests_run += 1

    errors = False

    MUSIC_outfiles = MUSIC_outfiles_L0 if self.current_level == 0 else MUSIC_outfiles_Lgt0

    try:
        assert(exists(self.music_conf_name))
    except AssertionError as e:
        fail(self, f"{self.music_conf_name} not found")
        errors = True

    for fname in MUSIC_outfiles:
        try:
            assert(exists(fname))
        except AssertionError as e:
            fail(self, f"{fname} not found in {os.getcwd()}.")
            errors = True
        # end try
    # end for

    if errors: return
    
    self.tests_passed += 1
    succeed(self)

def test_enzo_config_matches_solution(self):
    self.tests_run += 1
    errors = False
    solution_file = f"{self.test_solutions_dir}/{self.simulation_name}{self.level_suffix}.enzo"

    generated_file = f"{self.level_dir}/{self.enzo_conf_name}"

    try: 
        assert(filecmp.cmp(generated_file, solution_file, shallow=False))
    except AssertionError as e:
        fail(self, f"{generated_file} does not match solution file at {solution_file}")
        errors = True
    except FileNotFoundError as e:
        fail(self, f"{e.filename} does not exist.")
        errors = True

    if errors: return

    self.tests_passed += 1
    succeed(self)

# This list does not capture all of the enzo outputs,
# just the ones we care about
enzo_outdirs = [
    "RD0000",
    "RD0076"
]

enzo_outfiles = [
    "RunFinished"
]

def fake_enzo_run(self):
    for dname in enzo_outdirs:
        src = f"{self.test_solutions_dir}/{dname}"
        dst = f"{self.level_dir}/{dname}"
        try :
            copytree(src, dst)
        except FileExistsError as e:
            # if the file already exists then we dont need to do anything
            pass

    for fname in enzo_outfiles:
        src = f"{self.test_solutions_dir}/{fname}"
        dst = f"{self.level_dir}/{fname}"
        copyfile(src, dst)

def test_run_enzo(self):
    self.tests_run += 1

    errors = False

    try:
        assert(exists(self.enzo_conf_name))
    except AssertionError as e:
        fail(self, f"{self.enzo_conf_name} not found")
        errors = True

    for dname in enzo_outdirs:
        generated_file = f"{self.level_dir}/{dname}/{dname}"

        try: 
            assert(exists(generated_file))
        except AssertionError as e:
            fail(self, f"{generated_file} does not exist.")
            return
    # end for

    for fname in enzo_outfiles:
        try:
            assert(exists(f"{fname}"))
        except AssertionError as e:
            fail(self, f"{fname} not found in {os.getcwd()}.")
            errors = True
        # end try
    # end for

    if errors: return
    
    self.tests_passed += 1
    succeed(self)

def test_region_point_file_creation(self):
    self.tests_run += 1
    errors = False

    solution_file = f"{self.test_solutions_dir}/halo_{self.halo_id}_region_point_file{self.level_suffix}"
    generated_file = self.region_point_file
        
       
    nparticles_in_solution = 0
    with open(solution_file, 'r') as solution:
        for line in solution:
            nparticles_in_solution += 1

    nparticles_in_generated = 0
    try:
        with open(generated_file, 'r') as generated_file:
            for line in generated_file:
                nparticles_in_generated += 1

        assert(nparticles_in_solution == nparticles_in_generated)
    except FileNotFoundError as e:
        fail(self, f"{e.filename} not found")
        errors = True
    except AssertionError:
        fail(self, f"{nparticles_in_generated} particles found. Solution contains {nparticles_in_solution} particles")
        errors = True

    if errors: return
    
    self.tests_passed += 1
    succeed(self)

def fake_particle_run(self):

    fname = basename(self.region_point_file)
    
    src = f"{self.test_solutions_dir}/{fname}"
    dst = f"{self.level_dir}/{fname}"
    copyfile(src, dst)

# Stub method for tests that have not yet been implemented but might be someday...
def test_not_implemented(self):
    self.tests_run += 1
    errors = False
    
    fail(self, "Test has not yet been implemented")
    errors = True

    if errors: return
    
    self.tests_passed += 1
    succeed(self)