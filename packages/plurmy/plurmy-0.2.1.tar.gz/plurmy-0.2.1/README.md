# Python + Slurm = Plurmy

[![Documentation Status](https://readthedocs.org/projects/plurmy/badge/?version=latest)](https://plurmy.readthedocs.io/en/latest/?badge=latest)

This project was born out of an apparent lack of a library for job submission to slurm clusters. We sought to write a simple, low-level library with an API that mirrors the slurm `sbatch` command line tool. Plurmy is the result of that.

## Usage
We envision this library being used primarily through the `Slurm` class. This class uses attributes, named identically to full length `#SBATCH` arguments. For example:

```python
from plurmy import Slurm
command = 'srun -n 3 python my_super_script.py"
myjob = Slurm(time="00:10:00", partition="research", ntask=3)
myjob.submit()
```