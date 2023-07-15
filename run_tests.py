import csv
import json
from pathlib import Path
from subprocess import PIPE, DEVNULL
from typing import *
from lamb.utils.TempFile import make_tempfile
import asyncio

import textwrap
from tqdm.asyncio import tqdm_asyncio
import argparse

parser = argparse.ArgumentParser(description='Run evaluation tests.')
benchmark_range_group = parser.add_mutually_exclusive_group()
benchmark_range_group.add_argument('-a', '--all', action='store_true',
                    help='enable long-running testcases of SASS and Python')
benchmark_range_group.add_argument('-f', '--fastest', action='store_true',
                    help='only run the fastest testcase from each grammar')
parser.add_argument('-t', '--timeout', metavar='timeout', type=int, default=3600,
                    help='timeout for each case, in seconds')

prog_args = parser.parse_args()

app_root = Path(__file__).absolute().parents[0]
tests_root = app_root / 'tests/checker-benchmark/'
all_tests = [
        tests_root / 'yaml',
        tests_root / 'fsharp-snippet',
        tests_root / 'haskell-snippet',
        ]

if prog_args.all:
    print('[INFO] Running all tests, including SASS and Python.')
    all_tests += [tests_root / 'sass', tests_root / 'python']
elif prog_args.fastest:
    print('[INFO] only running the fastest testcase from each grammar')
    all_tests = [tests_root / 'fastest']
else:
    print('[INFO] Skipping SASS and Python testcases by default. Use --all to enable them.')


print_lock = asyncio.Lock()


async def run_on_case(grammar_path, start_var=None):
    """Run Lamb with the provided grammar and parses the output.
    """
    args = ['-m', 'lamb', '-c', '20', '-s', '-b', grammar_path]
    if start_var is not None:
        args.extend(['-v', start_var])
    fp = make_tempfile('w', '.in')
    print('list rule\nshow sentence', file=fp)
    fp.close()
    fp = open(fp.name, 'r')
    try:
        proc = await asyncio.subprocess.create_subprocess_exec(
            'python', *args, stdin=fp, stdout=PIPE, stderr=DEVNULL)
        stdout, _ = await asyncio.wait_for(proc.communicate(), prog_args.timeout)
        return stdout, True
    except TimeoutError:
        return b'', False


def decode_output(output: bytes) -> List[Dict[str, Any]]:
    out_list = output.decode('utf-8').split('\n')
    result = []
    for line in out_list:
        try:
            result.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return result


async def ambiguous_main(cases: List[Path]):
    sched_variants = []
    bnf_names = []
    for folder in cases:
        for bnf in folder.glob('*.bnf'):
            sched_variants.append(run_on_case(bnf))
            bnf_names.append(bnf)

    results = await tqdm_asyncio.gather(*sched_variants)

    total, passed = 0, 0
    fail_list = []
    collected_results = []
    for (output, res), bnf in zip(results, bnf_names):
        total += 1
        decoded_output = decode_output(output)

        case_name = "/".join(bnf.parts[-2:])
        try:
            async with print_lock:
                print(f'- executing on {case_name}')
                fail_list.append(case_name)
                if not res:
                    print(f'  [❌] timeout on testcase {bnf}')
                    continue
                valid = True
                msg = 'ok'
                try:
                    # Next, we shall compute metrics
                    metrics = extract_ambiguous_results(decoded_output)

                    collected_results.append(
                        (str(case_name), metrics)
                    )
                    print(textwrap.indent(str(metrics), ' ' * 2))
                except Exception as e:
                    valid = False
                    msg = f'Failed to collect metrics: {e}'

                if valid:
                    print(f'  [✅] {msg}')
                    fail_list.pop()
                    passed += 1
                else:
                    print(f'  [❌] {msg}')
                    continue

        except Exception as e:
            print(f'- executing on {case_name}')
            print(f'  [❌] {e}')

    print(f'Passed: {passed} of {total}')
    print('Failed cases:', fail_list)
    with (app_root / 'result.csv').open('w') as f:
        writer = csv.writer(f)
        writer.writerow(['Case', 'Formula Construction Time', 'Solving Time', '# LS2NF rule', 'Ambiguous sentence length'])
        for case_name, metrics in collected_results:
            writer.writerow([case_name, metrics['other_time'], metrics['solve_time'],
                metrics['ls2nf_rule_cnt'], metrics['found_len']])
        for case_name in fail_list:
            writer.writerow(([case_name, 'N/A', 'N/A', 'N/A', 'N/A']))


def extract_ambiguous_results(decoded_output):
    solve_time, other_time = .0, .0
    ls2nf_rule_cnt = 0
    found_len = -1
    sentence = None
    for line in decoded_output:
        if line['type'] == 'time':
            t = line['data']['time']
            if line['data']['name'] == 'solve':
                solve_time += t
            else:
                other_time += t
        elif line['type'] == 'list' and line['data']['name'] == 'rule':
            ls2nf_rule_cnt = len(line['data']['rule'])
        elif line['type'] == 'found':
            found_len = line['data']['length']
        elif line['type'] == 'sentence':
            sentence = line['data']['sentence']
    return {
            'solve_time': solve_time,
            'other_time': other_time,
            'found_len': found_len,
            'ls2nf_rule_cnt': ls2nf_rule_cnt,
            'sentence': sentence,
            }

    
if __name__ == '__main__':
    asyncio.run(ambiguous_main(all_tests))
