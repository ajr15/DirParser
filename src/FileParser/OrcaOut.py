from .FileParser import FileParser

class OrcaOut (FileParser):

    """A file parser for ORCA standard output files"""
    extension = "out"

    def read_scalar_data(self):
        """Method to read basic properties from ORCA output.
        ARGS:
            NONE
        RETURNS:
            (dict) dictionary with properties
                    {
                        "runtime": (float) runtime in seconds,
                        "final_energy": (float) final energy in Hartree,
                        "finished_normally": (bool) wheather computation finished without errors
                    }"""
        outdict = {
            "runtime": None,
            "final_energy": None,
            "finished_normally": False
        }
        with open(self.path, "r") as f:
            for line in f.readlines():
                if "FINAL SINGLE POINT ENERGY" in line:
                    if "Wavefunction not fully converged!" in line:
                        print("WARNING: SCF didn't fully converge in {}".format(self.path))
                    outdict['final_energy'] = float(line.split()[4])
                if "Sum of individual times" in line:
                    outdict['runtime'] = float(line.split()[5])
                if "****ORCA TERMINATED NORMALLY****" in line:
                    outdict["finished_normally"] = True
        return outdict

    def _read_mol_dict(self):
        outdict = {
            "atom_symbols": None,
            "atom_coords": None,
            "bondmap": None
        }

        with open(self.path, "r") as f:
            MoleculeBlock = False
            for line in f.readlines():
                if "CARTESIAN COORDINATES (ANGSTROEM)" in line:
                    MoleculeBlock = True
                    outdict['atom_symbols'] = []
                    outdict['atom_coords'] = []
                    continue
                if "--------" in line:
                    continue
                if len(line) < 2:
                    MoleculeBlock = False
                if MoleculeBlock:
                    v = line.split()
                    outdict['atom_symbols'].append(v[0])
                    outdict['atom_coords'].append([float(x) for x in v[-3:]])
        return outdict