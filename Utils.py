import sys

def pypy_notice() -> None:
    if not sys.implementation.name.startswith('pypy'):
        print('\n*****\nUsing pypy is recommended for performance.\n*****\n')