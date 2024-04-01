import argparse
import json
import math
import numpy as np
import random
import sympy as sp

random.seed(42)

# XOR Sampling algorithm


def sample_true():
    """
    Returns:
     - True or False with probability 0.5 each.
    """
    if random.random() < 0.5:
        return (True)
    return (False)


def sample_one_xor(q, n):
    """
    Independently choose each point i with probability q to form XOR statement.

    Parameters:
    - q: probability of independently choosing each point i for XOR constraint
    - n: number of points to choose from

    Returns:
    - one XOR constraint

    """
    xors = []

    for i in range(1, n+1):
        # Randomly choose whether to include the point i in XOR
        if random.random() < q:  # not sure whether <= q or <q
            xors.append(i)

    return xors


def generate_xor_constraints(s, q, n):
    """
    Generates s random xor constraints

    Parameters:
    - s: number of random XOR constraints to be added
    - q: probability of independently choosing each point i for XOR constraint
    - n: number of points to choose from

    Returns:
    - list of s XOR constraints

    """
    random_constraints = []
    for i in range(s):
        random_constraints.append([sample_one_xor(q, n), sample_true()])
    return random_constraints


# LinMod Sampling algorithm

def factorize(a, f, d):
    """
    Factorize a number a into at most d factors, each less than or equal to f.

    Parameters:
    - a: integer to factorize
    - f: largest possible factor
    - d: maximum number of factors

    Returns:
    - list F of factors

    """
    F = []
    while a > 1 and f > 1:
        while a % f == 0:
            F.append(f)
            a //= f
        f -= 1

    if a == 1 and len(F) <= d:
        return F
    else:
        return []


def partition(lambda_val, p):
    """
    Compute a suitably accurate combination of linear modular equalities and
    inequalities to restrict the search space to a cell of the desired size,
    given by the sample faction lambda_val.

    Parameters:
    - lambda_val: sample fraction
    - p: modulus (prime number)

    Returns:
    - number of constrants m
    - list of factors F

    """

    F = []

    nu_max = 100  # set in their experiments
    epsilon = 0.01  # set in their experiments
    nu = nu_max + 1  # initialization for most outest loop, will be overwritten

    while nu > nu_max:
        m = 0
        nu = lambda_val

        while len(F) == 0:
            m += 1
            nu *= p

            if abs(nu - 1) / nu <= epsilon:
                return m, F

            if nu > nu_max:
                break

            if (nu - math.floor(nu)) / nu <= epsilon:
                F = factorize(math.floor(nu), p - 1, m)

            elif len(F) == 0 and (math.ceil(nu) - nu) / nu <= epsilon:
                F = factorize(math.ceil(nu), p - 1, m)

        epsilon *= 2

    return m, F


def generate_linmod_constraints(lambda_val, l, len_x):
    """
    Generate random linear modular equation constraints to cut the solution
    space.

    Parameters:
    - lambda_val: sample fraction
    - l: largest domain value among sample variables
    - len_x: number of problem variables

    Returns:
    - matrix A1, vector b1 representing equality constraint
    - matrix A, vector b, vector c representing inequality constraint
    - p - prime number to be used in linear modular constraints

    """

    p = sp.nextprime(max(l, 5))
    m, F = partition(lambda_val, p)
    m_less = len(F)
    m_equal = m - m_less

    A1 = []
    b1 = []
    A = []
    b = []
    c = []

    if m_equal > 0:
        for i in range(1, m_equal + 1):

            b1.append(random.randint(0, p - 1))

            A1_i = []

            for j in range(len_x):
                A1_i.append(random.randint(0, p - 1))

            A1.append(A1_i)

    if m_less > 0:
        for i in range(1, m_less + 1):

            f = F.pop(0)
            c.append(f - 1)
            b.append(random.randint(0, p - 1))

            A_i = []

            for j in range(len_x):
                A_i.append(random.randint(0, p - 1))

            A.append(A_i)

    return A1, b1, A, b, c, p


def get_par_dict():
    """
    Specifies the parameter values of the base model and returns them in a dictionary.

    Returns:
    - parameters_dict: Dictionary containing the parameters of the base model

    """
    # Specify parameters of the problem
    matrix = np.loadtxt(open("euclidean_mat_5000m.csv",
                        "rb"), delimiter=",", skiprows=1)
    matrix = np.around(matrix).tolist()

    n = len(matrix)  # length of matrix
    k = 6  # number of points to look for
    d = 2000  # minimum euclidean distance btw points

    parameters_dict = {
        'n': n,
        'k': k,
        'd': d,
        'M': matrix
    }

    return parameters_dict


def xor_sampling_experiment(iterations):
    """
    Generates the constraints for many runs of the XOR sampling algorithm. Writes constraints to a .json file
    and the conjure solve commands to a .txt file.

    """

    parameters_dict = get_par_dict()

    # Define number of runs of the experiment
    pivot_s = math.floor(math.log2(num_sols))  # pivot value

    # Generate XOR constraints for each run

    for s in range(0, pivot_s + 2, 1):  # vary values of s

        for i in range(iterations):

            parameters_dict['constraints'] = generate_xor_constraints(s, q, parameters_dict['n'])

            filename = parameter_files_dir + "/s_" + \
                str(s) + "_" + str(i) + ".json"

            # write to json
            with open(filename, "w") as outfile:
                json.dump(parameters_dict, outfile)

            # add conjure solve command to commands txt
            commands_file.write("conjure solve models/xor_sampling_model.essence " + filename + " --output-format=json --solutions-in-one-file --solver=kissat --output-directory=\"" +
                                conjure_output_dir + "\" --number-of-solutions=all  --savilerow-options \"-O3 -sat-sum-tree\"\n")

            print(f's: {s}, iteration: {i}, written to file.')


def linmod_sampling_experiment(iterations):
    """
    Generates the constraints for many runs of the Lin Mod sampling algorithm. Writes constraints to a .json file
    and the conjure solve commands to a .txt file.

    """

    parameters_dict = get_par_dict()

    # Define number of runs of the experiment
    pivot_lambda = 1 / num_sols
    lambda_vals = np.unique(np.linspace(
        0.5 * pivot_lambda, 2 * pivot_lambda, 10, endpoint=True).round(decimals=2))

    # Generate linear modular constraints for each run

    for lambda_ in lambda_vals:  # vary values of lambda

        for i in range(iterations):

            A_eq, b_eq, A_ineq, b_ineq, c, p = generate_linmod_constraints(
                lambda_, parameters_dict['n'], parameters_dict['k'])

            m_eq = len(A_eq)
            m_ineq = len(A_ineq)

            parameters_dict['m_eq'] = m_eq
            parameters_dict['m_ineq'] = m_ineq
            parameters_dict['A_eq'] = A_eq
            parameters_dict['b_eq'] = b_eq
            parameters_dict['A_ineq'] = A_ineq
            parameters_dict['b_ineq'] = b_ineq
            parameters_dict['c'] = c
            parameters_dict['p'] = p

            filename = parameter_files_dir + "/lambda_" + \
                str(lambda_) + "_" + str(i) + ".json"

            # write to json
            with open(filename, "w") as outfile:
                json.dump(parameters_dict, outfile)

            # add conjure solve command to commands txt
            commands_file.write("conjure solve models/linmod_sampling_model.essence " + filename +
                                " --output-format=json --solutions-in-one-file --output-directory=\"" + conjure_output_dir + "\" --number-of-solutions=all\n")
            
            print(f'lambda: {lambda_}, iteration: {i}, written to file.')

def no_sampling_experiment(iterations):
    """
    Writes base model parameters to .json files. Writes the conjure solve commands to solve the base model
    to a .txt file.

    """
    parameters_dict = get_par_dict()

    # Create multiple JSON files so that output files in output directory have different names and can be analysed
    for i in range(iterations):

        filename = parameter_files_dir + "/base_pars_" + str(i) + ".json"

        # write to json
        with open(filename, "w") as outfile:
            json.dump(parameters_dict, outfile)

        # add conjure solve command to commands txt
        commands_file.write("conjure solve models/base_model.essence " + filename +
                            " --output-format=json --solutions-in-one-file --output-directory=\"" + conjure_output_dir + "\" --number-of-solutions=1\n")
        
        print(f'iteration: {i}, written to file.')

# Read and parse command line arguments
parser = argparse.ArgumentParser(description="This is the experiment setup.")

parser.add_argument("-solutions_flag", "--solutions", action="store_true",
                    help="Set flag for experiment to record solutions instead of performance")
parser.add_argument("num_sols", type=int,
                    help="Number of solutions to problem")
parser.add_argument("sampling_algorithm", type=str, help="xor or linmod")
parser.add_argument("commands_file", type=argparse.FileType(
    'w'), help="Txt file to store the conjure solve commands")
parser.add_argument("conjure_output_dir", type=str,
                    help="Output directory for conjure files without /")
parser.add_argument("parameter_files_dir", type=str,
                    help="Directory for generated parameter files without /")

args = parser.parse_args()

solutions_flag = args.solutions
num_sols = args.num_sols
sampling_algorithm = args.sampling_algorithm
commands_file = args.commands_file
conjure_output_dir = args.conjure_output_dir
parameter_files_dir = args.parameter_files_dir
q = 0.5

# Depending on whether to record solutions or runtime, change number of iterations
if solutions_flag:
    iterations = 100 * num_sols
else:
    iterations = 30

# Depending on sampling algorithm
if sampling_algorithm == 'xor':
    xor_sampling_experiment(iterations)
elif sampling_algorithm == 'linmod':
    linmod_sampling_experiment(iterations)
else:
    no_sampling_experiment(iterations)
