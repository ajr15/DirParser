from .FileParser import FileParser
from ..base.Structure import Structure
from ..utils.utils import generate_unique_id
from pymatgen.core.periodic_table import Element
import warnings
from typing import List
import os

class AbinitIn (FileParser):
    extension = "abi"


    def read_scalar_data(self):
        raise NotImplementedError("read_scalar_data is not implemented yet for AbinitIn files")


    def read_specie(self):
        raise NotImplementedError("read_specie is not implemented yet for AbinitIn files")


    def _format_kwdict(self, kwdict: dict):
        """Method to reformat keywords dictionary"""
        # copying kwdict to prevent override problems
        nkwdict = {}
        if not "pp_dirpath" in kwdict:
            raise ValueError("Must put pp_dirpath (path to directory with pseudo ")
        if not "autoparal" in kwdict:
            warnings.warn("No parallelization option found, adding one automatically. if you dont want parallelization, set \'autoparal\'=0 in kwdict")
            nkwdict["autoparal"] = 1
        for k, v in kwdict.items():
            if k in ["acell", "rprim", "ntypat", "znucl", "natom", "typat", "xred"]:
                warnings.warn("{} is specified in keywords dictionary but is determined automatically. It will be overwritten.".format(k))
            elif k == "temp_dir":
                nkwdict["tmpdata_prefix"] = os.path.join(v, str(generate_unique_id()))
            else:
                nkwdict[k] = v if not type(v) is str else "\"" + v + "\""
        return nkwdict

    
    def _make_pp_input_str(self, atom_types: List[str], kwdict: dict):
        if not "pseudos" in kwdict:
            warnings.warn("\'pseudos\' is not in the keywords dictionary, using default values")
            return " ".join([s + ".psp8" for s in atom_types])
        else:
            if not type(kwdict["pseudos"]) is dict:
                raise ValueError("value of \'pseudos\' keyword must by a dictionary with atom symbols (keys) and pseudo name (values)")
            else:
                pp_list = []
                for sym in atom_types:
                    if not sym in kwdict["pseudos"]:
                        warnings.warn("\'pseudos\' is not defined for {}, using default values".format(sym))
                        pp_list.append(sym)
                    else:
                        pp_list.append(kwdict["pseudos"][sym])
                return " ".join(pp_list)


    def write_file(self, structure: Structure, kwdict: dict):
        """Write input file from Structure object and kwdict (look at documentation for details)"""
        nkwdict = self._format_kwdict(kwdict)
        with open(self.path, "w") as f:
            # writing geometry keyworkds
            # defining unit cell
            f.write("# unit cell definition\n")
            f.write("acell {} {} {}\n".format(structure.lattice.a, structure.lattice.b, structure.lattice.c))
            f.write("rprim {}\n".format("\n".join([" ".join([str(s) for s in v]) for v in structure.lattice.vectors])))
            # defining atom types
            f.write("\n# setting atom types\n")
            atom_types = structure.get_atom_types()
            f.write("ntypat {}\n".format(len(atom_types)))
            f.write("znucl {}\n".format(" ".join([str(Element(sym).Z) for sym in atom_types])))
            # defining psuedo potentials
            f.write("\n# setting psuedopotentials\n")
            f.write(self._make_pp_input_str(atom_types, kwdict) + "\n")
            # defining atoms
            f.write("\n# setting atom coordinats\n")
            f.write("natom {}\n".format(len(structure.atoms)))
            f.write("typat {}\n".format(" ".join([str(atom_types.index(atom.symbol)) for atom in structure.atoms])))
            # defining coordinates
            f.write("xred\n")
            f.write("\n".join([" ".join([str(s) for s in structure.lattice.reduce_coordinates(atom.coordinates)])
                                             for atom in structure.atoms]))
            # writing calculation keywords
            f.write("\n# setting calculation keywords\n")
            for k, v in nkwdict.items():
                f.write(k + " " + str(v) + "\n")