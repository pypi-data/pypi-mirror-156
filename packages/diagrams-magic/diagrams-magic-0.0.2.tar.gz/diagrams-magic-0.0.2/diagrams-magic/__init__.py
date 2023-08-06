from IPython.core.interactiveshell import InteractiveShell
from IPython.display import display, SVG
from os import remove
from subprocess import check_output, call, SubprocessError
import platform
from shutil import which
from datetime import date

def diagrams(line: str, cell: str):
    if which('diagrams') is None:
        return 'error: diagrams command not installed'

    drivers = {'flowchart', 'dot', 'sequence', 'railroad'}
    tokens = line.strip().split(maxsplit=1)
    driver = tokens[0]
    if driver not in drivers:
        return 'use as: %%diagrams <driver name>, supported drivers are {:s}'.format(str(drivers))

    named = tokens[1] if len(tokens) == 2 else False
    now = str(date.today())
    src = now + '-src.txt'
    dest = (tokens[1] + '.svg') if named else now + '-dest.svg'

    with open(src, 'w') as desc:
        desc.write(cell)

    args = ['diagrams', driver, src, dest]
    if platform.system().lower() == 'windows':
        args[0] = 'diagrams.cmd'
    if platform.system().lower() == 'linux' and (driver == 'flowchart' or driver == 'sequence'):
        try:
            DISPLAY = check_output(['echo ${DISPLAY}', '-l'], shell=True).decode('utf-8')
        except SubprocessError as e:
            DISPLAY = ''
        
        if DISPLAY == '\n':
            if which('xvfb-run') is None:
                return 'cannot find (virtual) display, contact the server host for this'
            else:    
                args.insert(0, 'xvfb-run')

    # cmd = ' '.join(tokens)
    # system(cmd)
    call(args)
    
    with open(dest, 'rb') as pic:
        raw = pic.read()
    remove(src)
    if not named:
        remove(dest)
    
    return display(SVG(raw))

def load_ipython_extension(ipython: InteractiveShell):
    ipython.register_magic_function(diagrams, 'cell')
