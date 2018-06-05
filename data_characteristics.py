import glob
import pandas as pd
import numpy as np

full_data_files = glob.glob('data/*/*.data')
data_files = [d.split('/')[2].split('.')[0] for d in full_data_files]

data_list = list()
for d in full_data_files:
    name = d.split('/')[2].split('.')[0]
    # # BASH
    # command = ['wc', d, '-l']
    # f = subprocess.Popen(command, stdout=subprocess.PIPE).stdout
    # output = str(f.read().splitlines()[0])
    # lines, pathfile = output.split(' ')
    # # PANDAS
    df = pd.read_csv(d,
                     sep='\s+',
                     header=None)
    lines, columns = df.shape
    attribute = columns - 1  # Minus one because of target
    last_pos = attribute
    classes = np.unique(df[last_pos])
    n_classes = len(classes)
    distribution = tuple([len(df[df[last_pos] == c]) for c in classes])
    data_list.append({'Dataset': name,
                      'Size': lines,
                      'Attributes': attribute,
                      'Classes': n_classes,
                      'Class distribution': distribution})

pd.DataFrame(data_list).to_csv('data_characteristics.csv',
                               sep=';',
                               header=True,
                               columns=['Dataset',
                                        'Size',
                                        'Attributes',
                                        'Classes',
                                        'Class distribution'],
                               index=False)
