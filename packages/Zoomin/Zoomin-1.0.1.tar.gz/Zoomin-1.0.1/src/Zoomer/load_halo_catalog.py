
import numpy as np

class HaloData:

    def __init__(self, id, Mvir, Rvir, X, Y, Z, catalog_fname):
        self.id = int(id)
        self.Mvir = Mvir
        self.Rvir = Rvir
        self.X = X
        self.Y = Y
        self.Z = Z
        self.catalog_fname = catalog_fname

    def __repr__(self):
        return f"""
Halo {self.id}:
    Mvir : {self.Mvir:.5e} Msun
    Rvir : {self.Rvir:.7f}
    position : {self.X:.7f}, {self.Y:.7f}, {self.Z:.7f}
"""

##############################################################################
# Returns all halos in the ascii catalog in a dictionary indexed by the 
# halo id.
##############################################################################
def load_halo_catalog(self):
    # Units: Masses in Msun / h
    # Units: Radii in kpc / h (comoving)
    # Units: Positions in Mpc / h (comoving)
    #
    # Distances will be returned in code units, i.e. 
    # floating point numbers from 0 to 1, where 1
    # represents the full length of the box

    ids, DescID, Mvir, Vmax, Vrms, Rvir, Rs, Np, X, Y, Z, *other = np.genfromtxt(self.halo_catalog_file,
        skip_header=1,
        unpack=True)

    result = {}
    for i, halo_id in enumerate(ids):
        result[int(halo_id)] = HaloData(
            ids[i], 
            Mvir[i], 
            Rvir[i]/1000/self.box_length, 
            X[i]/self.box_length, 
            Y[i]/self.box_length, 
            Z[i]/self.box_length,
            self.halo_catalog_file)

    return result