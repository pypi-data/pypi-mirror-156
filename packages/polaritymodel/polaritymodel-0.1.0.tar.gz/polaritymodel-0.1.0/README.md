This is a pip-installable package containing all the code needed to run the cell polarity model, with all the modifications I've made of it.

Code (the bulk of `polarcore.py`) comes from this repo: [https://github.com/juliusbierk/polar](https://github.com/juliusbierk/polar). Prior work on this model can be found in these publications:

 - Nissen, S. B., Perera, M., Gonzalez, J. M., Morgani, S. M., Jensen, M. H., Sneppen, K., Brickman, J. M., & Trusina, A. (2017). Four simple rules that are sufficient to generate the mammalian blastocyst. PLoS Biology, 15(7), 1–30. https://doi.org/10.1371/journal.pbio.2000737
 - Nissen, S. B., Rønhild, S., Trusina, A., & Sneppen, K. (2018). Theoretical tool bridging cell polarities with development of robust morphologies. ELife, 7, 1–25. https://doi.org/10.7554/eLife.38407
 - Kirkegaard, J. B., Nielsen, B. F., Trusina, A., & Sneppen, K. (2019). Self-assembly, buckling and density-invariant growth of three-dimensional vascular networks. Journal of The Royal Society Interface, 16(159), 20190517. https://doi.org/10.1098/rsif.2019.0517
 - Nielsen, B. F., Nissen, S. B., Sneppen, K., Mathiesen, J., & Trusina, A. (2020). Model to Link Cell Shape and Polarity with Organogenesis. IScience, 23(2), 100830. https://doi.org/10.1016/j.isci.2020.100830

What this code does differently to what came before is to incorporate the effects of WNT expression on the orientation of planar cell polarity (PCP). WNT is a protein that has been observed to be important in organ formation, and in particular the formation of branched structures such as in the kidney, the lung, and salivary glands. We hypothesize that gradients of WNT expression act to orient PCP cyclically, promoting the formation and branching of stable tubular structures. Prior work has considered a two-dimensional model of organ formation, without PCP. We argue that PCP is key to understanding the role of WNT in branching for three-dimensional organs.

# Installation
To download and install this package, you can do:
1. Navigate to an empty folder
2. Run `gh repo clone jasnyder/polarpkg`
3. Run `python3 -m pip install .`

You can pass the `-e` flag to pip (i.e. run `python3 -m pip install -e .`), which will install the package in "editable" mode. This means that you can make changes to the source code and these changes will be immediately reflected in the code's behavior, without having to re-run `pip install`.

This should install the package. You should then be able to import it in Python by doing
```python
import polaritymodel
```

In the near-ish future (i.e. once I clean the code up enough) I will add this package to [PyPI](https://pypi.org/), at which point it can be installed by simply running
```
python3 -m pip install polaritymodel
```

# Requirements
The code relies essentially on `torch` for the heavy lifitng of the simulation, and benefits greatly from usage of a GPU. If your system does not support CUDA, be sure to run the code with the `device='cpu'` keyword (passed on creation of a `Polar`,`PolarWNT`, or `PolarPDE` object).

`numpy` is needed, as well as `scipy` mainly for its `KDTree` routine. Plotting is done with `plotly` which interacts with data via `pandas` DataFrames. `pickle` is used for data read/write.

# Usage
The basic usage of the code will look something like this
```python
from polaritymodel import PolarPDE, potentials_wnt

x, p, q = initial_conditions()
beta =
eta =
lam =
yield_every =

# set other params
timesteps = 10
yield_every = 10000

# create simulation object
sim = PolarPDE(x, p, q, beta, eta, lam, yield_every)

potential = potentials_wnt.potential_nematic_reweight
runner = sim.simulation(potential, timesteps, yield_every)

for line in itertools.islice(runner, timesteps):
    with open('path/to/data/file.pkl','wb') as fobj:
        pkl.dump(line, fobj)
```

## Plotting

Plotting is done via utilities in the `plot` subpackage. The `plot` subpackage has a core set of functions located in the module `plotcore`, and there are other modules to make different types of visualizations, such as 3D animations, heatmaps of ligand density, and PCP vector fields. These can be accessed from within a python script, such as
```python
from polaritymodel.plot.plotcore import load, build_df, select
from polaritymodel.plot.cones_wnt_ligand import plot, save
...
```
or alternatively from the command line, as such:
```
python3 -m polaritymodel.plot.cones_wnt
```
after which you will receive command-line prompts for the filename of the data set you wish to plot, and other relevant options.