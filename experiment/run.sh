# variables to set by user
SAMPLING_ALGORITHM="xor"
NUM_SOLS=22
COMMANDS_FILE="commands_xor.txt"
CONJURE_OUTPUT_DIR="conjure-output-xor"
PARAMETER_FILES_DIR="xor_constraints"
RESULTS_FILE="big_runtimes_xor.csv"

# installing python dependencies in a virtual environment
rm -rf myenv
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt

mkdir -p $PARAMETER_FILES_DIR
python3 gen_constraints.py $NUM_SOLS $SAMPLING_ALGORITHM $COMMANDS_FILE $CONJURE_OUTPUT_DIR $PARAMETER_FILES_DIR
parallel --no-notice --eta --results gnuparallel-results --joblog joblog.tsv :::: $COMMANDS_FILE
python3 record.py $NUM_SOLS $SAMPLING_ALGORITHM $RESULTS_FILE $CONJURE_OUTPUT_DIR

# getting out of the virtual environment
deactivate