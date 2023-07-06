import argparse

parser = argparse.ArgumentParser(prog='lamb', description='An ambiguity detector for layout-sensitive grammars.')
parser.add_argument('filename', metavar='filename', type=str, help='grammar file in Layout EBNF')
parser.add_argument('-d', '--debug', action='store_const', const=True,
                    default=False, help='enable debug output of rules')
parser.add_argument('-V', '--verbose', action='store_const', const=True,
                    default=False, help='enable verbose mode')
parser.add_argument('-s', '--serialize', action='store_const', const=True,
                    default=False, help='output serialized metrics')
parser.add_argument('-b', '--batch', action='store_const', const=True,
                    default=False, help='batch input mode; REPL PS1 strings will not be displayed')
parser.add_argument('-l', '--len', metavar='length', type=int, default=0,
                    help='start the verification process at the given word length')
parser.add_argument('-t', '--tabstop', metavar='tabstop', type=int, default=8, help='width of tab in spaces')
parser.add_argument('-v', '--start-var', metavar='start_var', type=str, default=None,
                    help='start variable of grammar; default to left side of the first production rule')
parser.add_argument('-c', '--check-bound', metavar='check_bound', type=int, default=None,
                    help='only check ambiguity; if specified, the grammar will be considered unambiguous after checking'
                         ' length = k where k is the bound given by this argument. returns 1 on ambiguity')

cmd_args = parser.parse_args()
_running_as_module = False

def set_running_as_module(val: bool):
    _running_as_module = val
