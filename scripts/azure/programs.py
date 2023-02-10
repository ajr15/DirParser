import os
from abc import ABC, abstractclassmethod

class Program (ABC):
	
	input_extension = None
	
	@abstractclassmethod
	def run_command(self, input_file: str) -> str:
		"""Method to make the run command to run the program on a node, given the input file"""
		pass
	
	
class Orca (Program):

	input_extension = ".inp"

	def __init__(self, orca_parent: str, use_hw: bool):
		self.orca_parent = orca_parent
		self.use_hw = 1 if use_hw else 0
		
	def run_command(self, input_file: str) -> str:
		"""Method to make the command for running ORCA on the server"""
		from azure_config import NODE_FILE_SHARE_MOUNT
		orca_run_script = NODE_FILE_SHARE_MOUNT + "/.azure-batch/scripts/run_orca.src"
		return "/bin/bash {} {} {}".format(orca_run_script, input_file, self.orca_parent, self.use_hw)