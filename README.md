# HADDOCK-antibody-antigen
[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0) 
[![Build Status](http://alembick.science.uu.nl:8080/buildStatus/icon?job=HADDOCK-antibody-antigen%2Fmaster&subject=Build%20duration:%20%24%7Bduration%7D)](http://alembick.science.uu.nl:8080/job/HADDOCK-antibody-antigen/) 
[![codecov](https://codecov.io/gh/haddocking/HADDOCK-antibody-antigen/branch/master/graph/badge.svg)](https://codecov.io/gh/haddocking/HADDOCK-antibody-antigen)

Here we provide the code to run the antibody protocol of **HADDOCK** by using the residues belonging to the *hypervariable* (**HV**) loops.
We use [ANARCI](http://opig.stats.ox.ac.uk/webapps/newsabdab/sabpred/anarci/) *[Dunbar, J. et al (2016). Nucleic Acids Res. 44. W474-W478]* to renumber the antibody according to the Chothia numbering scheme and to identify the HV loops.

## Installation
The easiest way is using [Conda](https://docs.conda.io/en/latest/miniconda.html) 
or its faster alternative [micromamba](https://github.com/mamba-org/mamba) that uses same API.

``` bash
git clone https://github.com/haddocking/HADDOCK-antibody-antigen.git
cd HADDOCK-antibody-antigen 

# Create conda enviroment from environment.yaml file:
micromamba env create -f environment.yaml
micromamba activate haddock-antibody
```

## Usage  

```bash
micromamba activate haddock-antibody 

# Renumber antibody with the Chothia scheme
python ImmunoPDB.py -i 4G6K.pdb -o 4G6K_ch.pdb --scheme c --fvonly --rename --splitscfv

# Format the antibody in order to fit the HADDOCK format requirements
# and extract the HV loop residues and save them into a file
python ab_haddock_format.py 4G6K_ch.pdb 4G6K-HADDOCK.pdb A > active.txt

# Add END and TER statements to the .pdb file
pdb_tidy 4G6K-HADDOCK.pdb > oo; mv oo 4G6K-HADDOCK.pdb
```