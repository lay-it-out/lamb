from lamb.interaction.cmd_args import get_cmd_args

formatter = {
    'time': '<b>{name}</b> took <ansiyellow>{time:04f}</ansiyellow> second(s).',
    'found': '\n***\n<ansigreen><b>Ambiguous sentence</b></ansigreen> of length <ansigreen><b>{length}</b></ansigreen> '
             'found. It shall be listed below.\n***\n',
    'word_len': 'Now checking witness sentences of length <ansiyellow>{length}</ansiyellow>...',
    'var_count': 'SMT variable count is <ansiyellow>{count}</ansiyellow>.',
    'check_false_positive': '<b>Found</b> a witness sentence, continue to check if it\'s a false positive.',
    'assertion_count': 'AST of the assertion <b>{name}</b> contains <ansiyellow>{count}</ansiyellow> nodes.',
    'deriv': '\n***\nFound <ansigreen><b>locally ambiguous variable</b></ansigreen>: '
                 '\"<ansigreen><b>{variable}</b></ansigreen>\". It corresponds to token(s) '
                 '<ansigreen><b>{interval}</b></ansigreen> in the ambiguous sentence.\n***\n',
    'repl': '\n<i>Now entering REPL...</i>\n'
}


def print_metric(obj):
    if get_cmd_args().serialize:
        import json
        print(json.dumps(obj))
    else:
        from prompt_toolkit import print_formatted_text
        from prompt_toolkit.formatted_text.html import HTML
        if 'data' in obj.keys():
            msg = formatter[obj['type']].format(**obj['data'])
        else:
            msg = formatter[obj['type']]
        print_formatted_text(HTML(msg))
