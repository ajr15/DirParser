import os
import shutil
import argparse
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(parent_dir)
from scripts.slurm import slurm_config

slurm_script = \
"""#!/bin/bash
#SBATCH --array=1-$n_tasks$
#SBATH --mem=$memory_per_task$
#SBATCH -n $cpus_per_task$
#SBATCH -N 1
#SBATCH -J $job_name$
#SBATCH --output=/dev/null

args_file=$args_file$
# get the i-th line of the param file
run_command=$(sed -n "$SLURM_ARRAY_TASK_ID"p "$args_file")

# running
$run_command"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Argument for task submission')
    parser.add_argument('TargetJob', type=str, help='The ID of the target job. For available jobs description, run with --list_jobs flag')
    parser.add_argument('TargetDirectory', type=str, help='Path to target directory with input files.')
    parser.add_argument('--cpus_per_task', type=int, default=16, help='Number of cpus for each input file')
    parser.add_argument('--memory_per_task', type=int, default=32, help='Number of RAM for each input file run (in GB)')
    parser.add_argument('--job_name', type=str, default="slurmJob", help='Name of the job')
    parser.add_argument('--list_jobs', action="store_true", help='Print the available jobs')
    args = parser.parse_args()
    job_id = args.TargetJob
    nwokers = args.cpus_per_task
    memory = args.memory_per_task
    job_name = args.job_name
    target_dir = args.TargetDirectory

    # pring job help if required
    if args.list_jobs:
        for k, v in azure_config.job_dict.items():
            print(k, v["help_msg"])
            import sys; sys.exit()

    if not job_id.lower() in slurm_config.job_dict:
        raise ValueError("Unrecognized job name {}, available job names {}".format(job_id, ", ".join(slurm_config.job_dict.keys())))

    # writing arguments file
    program = slurm_config.job_dict[job_id]["program"]
    n_inputs = 0
    with open(os.path.join(parent_dir, "scripts", "slurm", "tmp", "ars.txt"), "w") as f:
        for inp_file in os.listdir(target_dir):
            if inp_file.endswith(program.input_extension):
                n_inputs += 1
                f.write(program.run_command(os.path.join(target_dir, inp_file)) + "\n")
    # writing sbatch script
    script = slurm_script.replace("$n_tasks$", str(n_inputs))
    script = script.replace("$memory_per_task$", str(memory) + "GB")
    script = script.replace("$cpus_per_task$", str(nwokers))
    script = script.replace("$job_name$", str(job_name))
    script = script.replace("$args_file$", os.path.join(parent_dir, "scripts", "slurm", "tmp", "ars.txt"))
    with open(os.path.join(parent_dir, "scripts", "slurm", "tmp", "slurm.src"), "w") as f:
        f.write(script)
    # submitting
    os.system("sbatch {}".format(os.path.join(parent_dir, "scripts", "slurm", "tmp", "slurm.src")))