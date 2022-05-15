from re import sub
from typing import List
from time import sleep
from subprocess import run
import tempfile

_slurm_script = \
"""#!/bin/bash
#SBATCH --array=1-$n_tasks$
#SBATCH --mem=$memory_per_task$
#SBATCH -n $cpus_per_task$
#SBATCH -N 1
#SBATCH -J $job_name$
#SBATCH --output=/dev/null

args_file=$args_file$
# get the i-th line of the param file
run_command=$(sed -n "$SLURM_ARRAY_TASK_ID"p "$args_file")

# running
$run_command"""

class SlurmClient:

    """Method to submit command line tasks from python to SLURM cluster.
    ARGS:
        - cpus_per_task (int): number of cpus per task. default=1
        - memory_per_task (str): memory per task string. default='2GB'
        - job_name (str): job name to be displayed """

    def __init__(self, cpus_per_task: int=1, memory_per_task: str="2GB", job_name: str="slurm_job"):
        self.cpus_per_task = cpus_per_task
        self.memory_per_task = memory_per_task
        self.job_name = job_name
        self._job_ids = []

    def submit(self, cmds: List[str]):
        """Method to submit list of command line tasks to client"""
        # making temp submit file
        with tempfile.NamedTemporaryFile() as submit_f:
            # making temp arguments file
            with open("slurm_args.txt", "w") as args_f:
                # making string
                script = _slurm_script.replace("$n_tasks", str(len(cmds)))
                script = script.replace("$cpus_per_task$", str(self.cpus_per_task))
                script = script.replace("$memory_per_task$", str(self.memory_per_task))
                script = script.replace("$job_name$", str(self.job_name))
                script = script.replace("$args_file$", str("args.txt"))
                # writing string to file
                submit_f.write(script)
                # writing lines to argument file
                args_f.write("\n".join(cmds))
                # submitting file
                out = run("sbatch {}".format(submit_f.name), shell=True, capture_output=True, text=True)
                # capturing job ID
                self._job_ids.append(out.stdout.split(" ")[-1])

    def wait(self, update_time: int=1):
        """Method to wait until all client's jobs are finished.
        ARGS:
            - update_time (int): number of seconds to wait between checkups. default=1"""
        while True:
            # sleeps between each checkup
            sleep(update_time)
            # checks if all jobs are done
            _job_ids = []
            for job_id in self._job_ids:
                out = run("squeue -j {}".format(job_id), shell=True, capture_output=True, text=True)
                if len(out.stdout.split("\n")) > 1:
                    _job_ids.append(job_id)
            self._job_ids = _job_ids
            # if all jobs are done, break
            if len(self._job_ids) == 0:
                return