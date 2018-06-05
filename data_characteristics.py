import os
import subprocess
import glob

full_data_files = glob.glob('data/*/*.data')
data_files = [d.split('/')[2].split('.')[0] for d in full_data_files]

data_dict = dict()
for d in full_data_files:
    name = d.split('/')[2].split('.')[0]
    command = ['wc', d, '-l']
    f = subprocess.Popen(command, stdout=subprocess.PIPE).stdout
    output = str(f.read().splitlines()[0])
    print(output)
    lines, pathfile = output.split(' ')
    data_dict.update({name: {'lines': lines}})
