# Evaluating uniform solution sampling algorithms in constraint programming
University of St Andrews - Senior Honours Project 2024

This repo contains the work I did for my senior honours project on uniform solution sampling in constraint programming (CP). I assessed the sampling quality and runtime of two solution sampling algorithms, XORSample' [1] and LinMod [2], on one constraint satisfaction problem (CSP) from the field of ecology. 

## Problem
The constraint problem used is from the field of ecological sampling and aims to find independent sampling sites in the Cairngorms National Park. The independence criterion among sites is modelled through pairwise distance constraints. More specifically, we specify the CSP in the following way:

We want to obtain the placement of six (ten) recording devices to record bird sounds in the Cairngorms National Park, such that
- The devices are placed along a footpath network so that they are easily accessible by researchers.
- The devices are at least 1000m away from each other (euclidean distance) so that two sensors do not catch a sound simultaneously. We need this constraint to guarantee independent observations.

This problem specification is in the `base_model.essence` file in the `model` directory.

The `R` directory contains a script to extract random footpath coordinates from the Cairngorms shape data in the `spatial_data` directory and calculate a matrix of pairwise distances. I obtained two such matrices, `euclidean_mat_1000m.csv` and `euclidean_mat_5000m.csv` by changing the `dens` variable in the `make_dmat.R` script. The matrices will later be written to a parameter `.json` file to be an input to the conjure solvers.

## Implementation
The `experiments` directory contains the experiment setup. All result `.csv` files are in the `results` directory. An experiment can be run via the `run.sh` script, which contains all the necessary steps. The user can modify the different variables at the top of the script depending on the model used and the experiment to be conducted. The parameters are `SAMPLING_ALGORITHM`, `NUM_SOLS`, `COMMANDS_FILE`, `CONJURE_OUTPUT_DIR`, `PARAMETER_FILES_DIR`, `RESULTS_FILE`, and `SOL_FLAG`. `$SOL_FLAG="--solutions"` will record all solutions which can further be used to analyse the sampling quality, while `$SOL_FLAG=""` will record the runtimes. Besides these parameters, no changes to the `run.sh` script should be necessary for reconstructing my experiments. 

`run.sh` first creates a virtual environment using `venv` and installs the necessary `numpy`, `pandas`, and `sympy` modules.
The `gen_constraints.py` script includes the implementations of XORSample' [1] and LinMod [2] for the ecological problem. It generates the random constraints and writes them to parameter `.json` files in the `$PARAMETER_FILES_DIR` directory specified in `run.sh`. Furthermore, it creates the `$COMMANDS_FILE` containing all `conjure solve` commands to solve the problem instances in `$PARAMETER_FILES_DIR`. These commands are executed using GNU parallel. The `record.py` script records the output files stored in the `$CONJURE_OUTPUT_DICT` and returns a `.csv` `$RESULTS_FILE`.

I evaluated the algorithms' runtimes and sampling uniformity for different XORSample' and LinMod parameter values. These are hard-coded in `gen_constraints.py` and `record.py`. Furthermore, the variables defining the problem instance, i.e. the distance matrix, the minimum distance between recording devices etc., are hard-coded in `gen_constraints.py`.

The Python Notebooks in the `notebooks` directory contain the uniformity analysis and visualisations of the data.

## References

[1] Gomes, Carla & Sabharwal, Ashish & Selman, Bart. (2006). Near-Uniform Sampling of Combinatorial Spaces Using XOR Constraints.. Advances in Neural Information Processing Systems. 481-488. 

[2] Pesant, G., Quimper, CG., Verhaeghe, H. (2022). Practically Uniform Solution Sampling in Constraint Programming. In: Schaus, P. (eds) Integration of Constraint Programming, Artificial Intelligence, and Operations Research. CPAIOR 2022. Lecture Notes in Computer Science, vol 13292. Springer, Cham. https://doi.org/10.1007/978-3-031-08011-1_22


