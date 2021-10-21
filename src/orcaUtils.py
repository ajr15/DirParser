def ReadOutput(filename):
    """Method to read basic properties from ORCA output.
    ARGS:
        - filename (str): path to the out file
    RETURNS:
        (dict) dictionary with properties
                {
                    "runtime": (float) runtime in seconds,
                    "final_energy": (float) final energy in Hartree,
                    "atom_symbols": (list of strings) list of atom symbols,
                    "atom_coords": (list of 3-float vectors) list of atomic coordinates,
                    "finished_normally": (bool) wheather computation finished without errors
                }"""
    outdict = {
        "runtime": None,
        "final_energy": None,
        "atom_symbols": None,
        "atom_coords": None,
        "finished_normally": False
    }
    with open(filename, "r") as f:
        MoleculeBlock = False
        for line in f.readlines():
            if "FINAL SINGLE POINT ENERGY" in line:
                if "Wavefunction not fully converged!" in line:
                    print("WARNING: SCF didn't fully converge in {}".format(filename))
                outdict['final_energy'] = float(line.split()[4])
            if "Sum of individual times" in line:
                outdict['runtime'] = float(line.split()[5])
            if "****ORCA TERMINATED NORMALLY****" in line:
                outdict["finished_normally"] = True
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

def _gen_str_for_block(block_name: str, block_dict):
    s = "%{}\r".format(block_name.lower())
    for k, v in block_dict.items():
        s += "\t{} {}\r".format(k, str(v))
    s += "end\n\r"
    return s

def WriteInput(input_dict, filename):
    """Method to write input file to ORCA 4.2. Currently supports molecules only from xyz files or atoms + coords list
    ARGS:
        - input_dict (dict): 
                dictionary with ALL input parameters. General structure
                {
                    "top_kwds": [list with top kw strings],
                    "block1": {dict with variable names (keys) and their values (vals)},
                    ...
                    "molecule": dictionary to describe the input molecule
                                {
                                    "charge": (int),
                                    "multiplicity": (int),
                                    "xyzfile": (str path to xyz file with molecule),
                                    "atom_list": (list of atom symbols),
                                    "atom_coords": (list of atom coords as vectors)
                                }
                }
        - filename (str): path to the desired input file"""
    with open(filename, "w") as f:
        # write top kwds
        f.write("! " + " ".join(input_dict["top_kwds"]) + "\n\r")
        # write input blocks
        for k, v in input_dict.items():
            if not k in ['top_kwds', 'molecule']:
                f.write(_gen_str_for_block(k, v))
        # write molecule block
        d = input_dict['molecule']
        # write first line
        if 'xyzfile' in d.keys():
            f.write("* xyzfile {} {} {}".format(d['charge'], d['multiplicity'], d['xyzfile']))
        else:
            f.write("* xyz {} {}\n".format(d['charge'], d['multiplicity']))
            for s, v in zip(d['atom_list'], d['atom_coords']):
                f.write("  " + s + "  {}     {}     {}\n".format(round(v[0], 4), round(v[1], 4), round(v[2], 4)))
            f.write("*")


def test_inp_gen():
    kw_dict = {
        "top_kwds": ["B3LYP", "def2-SVP", "OPT", "Freq"],
        "basis": {'NewGTO Ni \"def2-TZVP\" end': ''},
        "scf": {"maxiter": 200},
        "pal": {"nprocs": 16},
        "molecule": {'charge': -1, 'multiplicity': 1, "xyzfile": './file.xyz'}
    }
    WriteInput(kw_dict, '.\\example.inp')

def main():
    d = ReadOutput(".\\subs_cryst_oxi.out")
    for k, v in d.items():
        print(k, v)

if __name__ == '__main__':
    main()