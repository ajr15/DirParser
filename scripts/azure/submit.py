"""Script to send a job to Azure Batch"""
try:
    import azure.batch as batch
    import azure.batch.batch_auth as batch_auth
except ImportError:
    raise ImportError("In order to use azure scripts you must have the \'azure\' package in your python environment")
import os
import argparse
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(parent_dir)
from scripts.azure import azure_config
from scripts.azure import programs


def get_task_idx():
	"""Makes a unique task id that is appended to its name. Used to allow tasks with the same name."""
	with open(os.path.join(parent_dir, "src", "utils", ".jobcount"), "r") as f:
		idx = int(f.read())
	with open(os.path.join(parent_dir, "src", "utils", ".jobcount"), "w") as f:
		f.write(str(idx + 1))
	return idx


def add_tasks(batch_service_client, job_name: str, program: programs.Program, target_dir: str) -> None:
	"""
	Adds a task for each input file in the collection to the specified job.
	ARGS:
		batch_service_client: A Batch service client.
		job_name (str): the name of the job (as appears in Azure Batch)
		program (programs.Program): a Program object describing the program on the node
		target_dir (str): target directory (contains all input files to run)
	"""
	tasks = list()
	local_target_dir = os.path.join(azure_config.local_mount_dir, target_dir.replace('/', '\\'))
	# submits tasks
	for input_file in os.listdir(local_target_dir):
		name = os.path.split(input_file)[-1][:-4]
		if input_file.endswith(".inp"):
			print("submitting {}".format(input_file))
			command = program.run_command(azure_config.mount_dir + target_dir + input_file)
			tasks.append(batch.models.TaskAddParameter(
				id="{}_{}".format(get_task_idx(), name),
				command_line=command
			)
			)
	batch_service_client.task.add_collection(job_id, tasks)
	

def format_target_dir(target_dir) -> str:
	"""Method to format the supplied target directory to the desired format"""
	# validation
	if "\\" in target_dir:
		raise ValueError("Supplied target directory must contain only / as separator (unix style path)")
	# formatting
	if not target_dir.startswith("/"):
		target_dir = "/" + target_dir
	if not target_dir.endswith("/"):
		target_dir = target_dir + "/"
	return target_dir


if __name__ == '__main__':
	# parse command line arguments
	parser = argparse.ArgumentParser(description='Argument for task submission')
	parser.add_argument('TargetJob', type=str, help='The ID of the target job. For available jobs description, run with --list_jobs flag')
	parser.add_argument('TargetDirectory', type=str, help='Path to target directory with input files. Path must be in Katarzyna1 fileshare parent dir as /')
	parser.add_argument('--list_jobs', action="store_true", help='Print the available jobs')
	args = parser.parse_args()
	job_id = args.TargetJob
	target_dir = args.TargetDirectory
	
	# pring job help if required
	if args.list_jobs:
		for k, v in azure_config.job_dict.items():
			print(k, v["help_msg"])
		import sys; sys.exit()
	
	# validate & formatting input parameters
	target_dir = format_target_dir(target_dir)
	if not job_id.lower() in azure_config.job_dict:
		raise ValueError("Unrecognized job name {}, available job names {}".format(job_id, ", ".join(azure_config.job_dict.keys())))

	# setup azure credentials
	credentials = batch_auth.SharedKeyCredentials(azure_config._BATCH_ACCOUNT_NAME,
													azure_config._BATCH_ACCOUNT_KEY)
	# configure batch client
	batch_client = batch.BatchServiceClient(
		credentials,
		batch_url=azure_config._BATCH_ACCOUNT_URL)
	# add tasks
	print("Adding tasks...")
	add_tasks(batch_client, job_id, azure_config.job_dict[job_id]["program"], target_dir)
	# finished
	print("Finished submission !")
	
