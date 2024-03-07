import argparse
import json
import math
import numpy as np
import pandas as pd
import os
import random

random.seed(10)  # p-value depends a lot on seed


def get_performance(performance_file):
    """
    Read the performance attributes from the .eprime-info file (performance file) and return them in a dictionary.

    Parameters:
    - performance_file: .eprime-info file 

    Returns:
    - a dictionary containing the different performance attributes and their values
    """
    if os.path.exists(performance_file):
        # Read performance file
        with open(performance_file, 'r') as file:
            lines = file.readlines()

        # Extract keys and values
        keys = [line.split(':')[0].strip() for line in lines]
        values = [line.split(':')[1].strip() for line in lines]

        # Create a dictionary
        new_row = {key: val for key, val in zip(keys, values)}

        return new_row
    else:
        return {}


def get_solution(data, l):
    """
    Get a solution from data (if there is any), which are the contents of the .solutions.json file
    and return it in a dictionary.

    Parameters:
    - data: file 
    - l: number of solutions returned by solver

    Returns:
    - a dictionary containing the found solution (if there is any)
    """

    # XOR sampling algorithm succeeds if there are more than 0 solutions.
    # LinMod Sampling algorithm only succeeds if there is one solution.
    if (l > 0 and sampling_algorithm == 'xor') or l == 1:
        # select random solution from remaining solutions
        index = random.randint(0, l - 1)
        solution = str(list(data[index]['y'].values()))

    else:
        solution = None

    return {'solution': solution}


def record(parameter, par_range):
    """
    Records the solution or the performance (depending on solutions_flag) from each run of the algorithm in a dataframe. 
    Writes the dataframe to a CSV file.

    Parameters:
    - parameter: the name of the parameter that we iterate over in the setup of the experiment. 
    's' for XOR, 'lambda' for linmod
    - par range: the range that this parameter should be iterated over
    """

    # Initialize dataframe
    if solutions_flag:
        df = pd.DataFrame(
            columns=[parameter, 'iteration', 'solution', 'num sols'])
    else:
        df = pd.DataFrame(columns=[parameter, 'iteration', 'num sols', 'SolverMemOut', 'SolverTotalTime', 'SATClauses',
                          'SavileRowClauseOut', 'SavileRowTotalTime', 'SolverSatisfiable', 'SavileRowTimeOut', 'SolverNodes', 'SATVars'])

    iterations = 100 * num_sols

    for par in par_range:

        for i in range(iterations):

            path = conjure_output_dir + "/model000001-" + \
                parameter + '_' + str(par) + "_" + str(i)
            solution_file = path + ".solutions.json"
            performance_file = path + ".eprime-info"

            if os.path.exists(solution_file):

                # Get number of solutions
                with open(solution_file, 'r') as file:
                    data = json.load(file)
                l = len(data)

                new_row = {parameter: par, 'iteration': i, 'num sols': l}

                if solutions_flag:
                    dict = get_solution(data, l)
                else:
                    dict = get_performance(performance_file)

                new_row.update(dict)

                df.loc[len(df)] = new_row

            else:
                print("File " + solution_file + " does not exist")

    # Write to csv file
    df.to_csv(results_file)


def record_xor_solutions():
    """
    Sets up the number of runs of the XOR algorithm and calls function to save solutions or performance in a csv file.
    """
    # Define number of runs of the experiment
    pivot_s = math.floor(math.log2(num_sols))  # pivot value
    par_range = range(0, pivot_s + 2, 1)  # vary values of s

    record('s', par_range)


def record_linmod_solutions():
    """
    Sets up the number of runs of the LinMod algorithm and calls function to save solutions or performance in a csv file.
    """
    # Define number of runs of the experiment
    pivot_lambda = 1 / num_sols
    par_range = np.unique(np.linspace(
        0.5 * pivot_lambda, 2 * pivot_lambda, 10, endpoint=True).round(decimals=2))

    record('lambda', par_range)


# Read and parse command-line arguments
parser = argparse.ArgumentParser(
    description="This is the experiment analysis.")

parser.add_argument("-solutions_flag", "--solutions", action="store_true",
                    help="Set flag for recording solutions instead of performance")
parser.add_argument("num_sols", type=int,
                    help="Number of solutions to problem")
parser.add_argument("sampling_algorithm", type=str, help="xor or linmod")
parser.add_argument("results_file", type=str,
                    help="Json filename to store results")
parser.add_argument("conjure_output_dir", type=str,
                    help="Output directory for conjure files without /")

args = parser.parse_args()

solutions_flag = args.solutions
num_sols = args.num_sols
sampling_algorithm = args.sampling_algorithm
results_file = args.results_file
conjure_output_dir = args.conjure_output_dir

if sampling_algorithm == 'xor':
    record_xor_solutions()
elif sampling_algorithm == 'linmod':
    record_linmod_solutions()
else:
    raise ValueError('only admissible inputs: xor, linmod')
