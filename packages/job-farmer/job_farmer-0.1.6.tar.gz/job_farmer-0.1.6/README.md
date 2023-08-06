# Job Farmer

[![PyPi version](https://badge.fury.io/py/job-farmer.svg)](https://pypi.org/project/job-farmer/)
[![PyPi Read the doc](https://img.shields.io/badge/doc-ReadTheDoc-0b72b7)](https://riffard.gitlab.io/job_farmer/read_the_doc/)
[![PyPi Pylint](https://riffard.gitlab.io/job_farmer/badges/pylint.svg)](https://riffard.gitlab.io/job_farmer/lint/)
[![PyPi Pipeline](https://gitlab.com/riffard/job_farmer/badges/main/pipeline.svg)](https://gitlab.com/riffard/job_farmer)
[![PyPi Coverage](https://riffard.gitlab.io/job_farmer/badges/coverage.svg)](https://riffard.gitlab.io/job_farmer/coverage/)

## Description

Job Farmer is a python API designed to prepare jobs for HPC platforms supporting SLURM.
It collects the job configurations of the associated tasks and prepares the task list and slurm configuration files
based on the system constraints and the required resources.

## Installation

### From PyPI

```bash
pip install job-farmer
```

### From sources

```bash
git clone git@gitlab.com:riffard/job_farmer.git
cd job_farmer
pip install .
```

## Usage

### Job configuration

In the file [`test/simple_job.py`](test/simple_job.py), we are showing a simple job submission.

First, you import the job-farmer:
```python
import job_farmer
```

Then you create the `System` object (NERSC/CORI-Haswell in this example) and the `Farmer` object
```python
system = job_farmer.CoriHaswell()

farmer = job_farmer.Farmer(system)
```

The nex step consists on creation the `JobConfiguration` and add it to the `Farmer`:
```python
job_configuration = job_farmer.JobConfiguration(name='test_job',
                       account='your_account',
                       queue='queue',
                       duration='xx:xx:xx')

farmer.add_global_job_configuration(job_configuration)
```

You add the `Tasks` to the `Farmer` and you link them to the job_configuration 
```python
task = job_farmer.Task(commands=[f'export MY_MESSAGE="Hello World!"',
                                 'echo "${MY_MESSAGE}"'], 
                        n_threads=1)
farmer.add_task(job_configuration.name, task)
```
    
And it builds the task list and the slurm configuration file:
```python
farmer.build()
```

Finally, you can submit the jobs to the batch system using:
```python
farmer.submit(dry_run = False)
```
(by default, `dry_run = True`).


**Note:** By default, the job-farmer logs are not displayed. 
To display them, you need to import the `logging` package and set the log level to `logging.INFO` such as:**
```python
logging.basicConfig(level=logging.INFO)
```

### Running jobs

#### Job runner


#### Batch submission


## Support

If you are encountering any issue, please open a git issue: [here](https://gitlab.com/riffard/job_farmer/-/issues)


## Contributing

Any contribution is more than welcome. To add any new feature, please follow this procedure: 

1. Create a git issue [here](https://gitlab.com/riffard/job_farmer/-/issues)
2. Create a new branch with the following format: `[initials]_[feature title]_issue_[issue number].`
3. Once the development is nearly completed, push the branch to the repository and create a merge request with the following guideline:
   1. The MR title must contain a short feature/bugfix  description
   2. The MR description must contain a detailed description of the feature/bug fix. Add here any relevant resources.
4. After reviewing the merge request, it will be merged to the `main` branch.


### Adding a new data center and a new system

1. To add a new data center, create a new python file in [`job_farmer/system`](job_farmer/system) 
with the name of the data center in the filename (use lower case).
2. To add a new system, add a new `System` class that inherits from `System` in the correct data center file.
To see an example, take a look at [`job_farmer/system/nersc.py`](job_farmer/system/nersc.py)



## License

This software is licenced under: [GNU Affero General Public License v3.0](LICENSE)
