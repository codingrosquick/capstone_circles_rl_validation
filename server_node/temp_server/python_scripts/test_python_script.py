# printing to sterr -- warning it requires python3
# source: https://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
from __future__ import print_function
import sys
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


# Passing in a parameter via the CLI?


# OK, when calling from JS, goes through if name is main
if __name__ == '__main__':
    arguments = sys.argv

    print(f'hi from stdout python before resolution. ARGUMENTS found are: {arguments}')

    # EXITING ON ERROR
    if  arguments[1] == 'err':
        eprint('error happening')
        sys.exit(1)

    # EXITING WITH 0 CODE
    sys.exit(0)

    # eprint('Hello from errors')
    # OK printing to stderr works