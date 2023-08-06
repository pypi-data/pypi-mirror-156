from std_usage import main
import sys

argv = [ 'python -m std_usage' ] + sys.arg[1:]
sys.exit(main(argv))
