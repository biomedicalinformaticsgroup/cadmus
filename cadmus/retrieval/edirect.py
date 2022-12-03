# import the necessary libraries
import sys
import shutil
import subprocess
import shlex

# here are the functions used by edirect
def execute(cmmd, data=""):
    if isinstance(cmmd, str):
        cmmd = shlex.split(cmmd)
    res = subprocess.run(cmmd, input=data,
                        capture_output=True,
                        encoding='UTF-8')
    return res.stdout.strip()

def pipeline(cmmds):
    def flatten(cmmd):
        if isinstance(cmmd, str):
            return cmmd
        else:
            return shlex.join(cmmd)
    if not isinstance(cmmds, str):
        cmmds = ' | '.join(map(flatten, cmmds))
    res = subprocess.run(cmmds, shell=True,
                        capture_output=True,
                        encoding='UTF-8')
    return res.stdout.strip()

def efetch(*, db, id, format, mode=""):
    cmmd = ('efetch', '-db', db, '-id', str(id), '-format', format)
    if mode:
        cmmd = cmmd + ('-mode', mode)
    return execute(cmmd)
