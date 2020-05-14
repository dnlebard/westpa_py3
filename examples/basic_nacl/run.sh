# Make sure environment is set
. ./env.sh

# Clean up
rm -f west.log

# Run w_run
w_run.py --work-manager processes "$@" &> west.log
