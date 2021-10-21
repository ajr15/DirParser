import argparse
import os
from importlib import import_module
import sys; sys.path.append("C:\\Users\\Shachar\\OneDrive - Technion\\Technion\\PhD\\Other Projects")
from DirParser.src.DirParser import DirParser

def get_type_from_str(type_str):
    try:
        pkg = import_module("DirParser.src.FileParser.{}".format(type_str, type_str))
        return getattr(pkg, type_str)
    except ImportError:
        raise ValueError("Unrecognized file type")

if __name__ == "__main__":
    # making command line input parser
    parser = argparse.ArgumentParser("A script for parsing an out directory")
    parser.add_argument("directoryPath", type=str, help="The path to the directory with files to parse")
    parser.add_argument("fileType", type=str, help="The name of the type of of the files in the directory. Must have same name as FileParser object")
    parser.add_argument("--create_mol_files", type=bool, default=False, help="(bool) Create a directory with molecule files (xyz, cif...)")
    parser.add_argument("--mol_file_ext", type=str, default="xyz", help="(str) molecule file extension. default=xyz")
    # setting user variables
    args = parser.parse_args()
    path = args.directoryPath
    file_parser = get_type_from_str(args.fileType)
    make_mol_files = args.create_mol_files
    # reading information from directory
    dir_parser = DirParser(file_parser)
    dir_parser.read_data(path)
    dir_parser.to_csv(os.path.join(path, "results.csv"))
    if make_mol_files:
        dir_parser.save_species(path, args.mol_file_ext)
    