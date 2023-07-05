import os
import shutil
from pathlib import Path

PATH = Path(os.path.expanduser('~/Documents/smt-disambig/tests/sass-redo2/'))

ls = os.listdir(PATH)
ls = list(filter(lambda x: x[:5] == 'round', ls))
ls.sort(key=lambda x: int(x[6:]))
last_id = int(ls[-1].split('-')[1])
new_folder = PATH / f'round-{last_id + 1}'
os.mkdir(new_folder)
shutil.copy(PATH / ls[-1] / f'sass.bnf', new_folder)
os.mknod(new_folder / f'sass.in')
os.mknod(new_folder / f'sass.out.yaml')
