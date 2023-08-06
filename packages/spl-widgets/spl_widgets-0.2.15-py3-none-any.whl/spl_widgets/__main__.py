from argparse import ArgumentParser, RawTextHelpFormatter
import importlib

parser_desc = "Run one of the python modules created by CTSF for the Barnard Speech Perception Laboratory"
arg_help = "(Positional) The module to run. Options: \
    \n\t- tuner \n\t- stk_swx \n\t- gorilla_clean \n\t- widgets_help \n\t- update_widgets"

parser = ArgumentParser(
    "runmod",
    description=parser_desc,
    formatter_class=RawTextHelpFormatter
)
parser.add_argument("mod", metavar="M", help=arg_help)

args = parser.parse_args()
cmd = args.mod

# Programmatically import and run the desired module, instead of importing everything
try:
    mod = importlib.import_module(cmd, "spl_widgets")
    main = getattr(mod, "main")
    main()
except ModuleNotFoundError:
    print("Bad command: " + repr(cmd))