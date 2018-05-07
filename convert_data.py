import os
import configparser
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

config_folder = 'datafiles/classification/'
processed_folder = 'processed/'
nested_folder = 'uci/'
error_files = list()
download_error = list()

if not os.path.isdir(processed_folder):
    os.mkdir(processed_folder)

if not os.path.isdir(nested_folder):
    os.mkdir(nested_folder)

# Folders from configuration
folders = os.listdir(config_folder)

# # Folders from errors
# folders = [line.rstrip('data\n')[:-1] for line in open('error_files.txt')]
# download_error = [line.rstrip('\n') for line in open('download_error.txt')]

separators = {'comma': ',',
              '': r'\s+'}

for directory in folders:
    config_file = None
    data_file = None
    full_dir = ''.join([config_folder, directory])
    if os.path.isdir(full_dir):
        for f in os.listdir(full_dir):
            if '.ini' in f:
                config_file = f
            elif '.data' in f:
                data_file = f
            else:
                pass
        if config_file is not None and data_file is not None:
            try:
                # Read config file
                config = configparser.ConfigParser()
                config.read('/'.join([full_dir, config_file]))
                sep = separators[config['info']['separator']]
                # Does it have index?
                index = config['info']['id_indices']
                if index == '':
                    index_col = None
                else:
                    index_col = int(index) - 1
                # Read data
                df = pd.read_csv('/'.join([full_dir, data_file]),
                                 sep=sep,
                                 index_col=index_col,
                                 header=None)
                # Remove NaN
                df = df.replace('?', np.nan)
                # Remove missing
                df = df.replace('', np.nan)
                # REMOVING
                # Removing depending on how many data are left out
                len_rm_rows = len(df.dropna(axis=0).index)  # Length when rows are removed
                len_rm_cols = len(df.dropna(axis=1).index)  # Length when columns are removed
                if len_rm_cols > len_rm_rows:
                    df = df.dropna(axis=1)
                else:
                    df = df.dropna(axis=0)
                # Changing label to last column
                final_column = df.columns[-1]
                label_column = int(config['info']['target_index']) - 1  # In python, index begins at 0
                if label_column != final_column:
                    if label_column not in df.columns:
                        raise KeyError('Label index {} is not in columns {}'.format(label_column, df.columns))
                    a = df[final_column]
                    df[final_column] = df[label_column]
                    df[label_column] = a

                if df[final_column].dtype != int and df[final_column].dtype != float:
                    le = LabelEncoder()
                    df[final_column] = le.fit_transform(df[final_column])

                for c in df.columns[:final_column]:
                    if df[c].dtype == float or df[c].dtype == int:  # It is a float, but it was parsed as int
                        df[c] = pd.Series(df[c], dtype=float)
                    else:  # It was a string, need to be transformed
                        le = LabelEncoder()
                        try:
                            df[c] = pd.Series(le.fit_transform(df[c]), dtype=float)
                        except Exception as e:
                            print(e)

                # Saving the dataframe into processed folder
                df.to_csv(''.join([processed_folder, data_file]), sep=' ', header=False, index=False)

                # Saving the dataframe into nested folder
                final_folder = ''.join([nested_folder, data_file.replace('.data', '')])
                if not os.path.isdir(final_folder):
                    os.mkdir(final_folder)
                df.to_csv('/'.join([final_folder, data_file]), sep=' ', header=False, index=False)

            except pd.errors.ParserError as e:
                print(' '.join([data_file, 'gives a parser error']))
                error_files.append(data_file)

            except UnicodeDecodeError as e:
                print(' '.join([data_file, 'gives an Unicode error']))
                error_files.append(data_file)

            except KeyError as e:
                print(' '.join([data_file, 'gives a KeyError']))
                error_files.append(data_file)

            except TypeError as e:
                print(' '.join([data_file, 'gives a TypeError']))
                error_files.append(data_file)

            except IndexError as e:
                print(' '.join([data_file, 'separator is not correct']))
                error_files.append(data_file)

        else:
            print('{} does not have .data and .ini files'.format(full_dir))
            download_error.append(full_dir)
    else:
        print('{} directory does not exist'.format(full_dir))
        download_error.append(full_dir)

with open('error_files.txt', 'w') as f:
    if len(error_files) > 0:
        for file in error_files:
           f.write(''.join([file, '\n']))
    else:
        f.write('\n')

with open('download_error.txt', 'w') as f:
    if len(download_error) > 0:
        for folder in download_error:
            f.write(''.join([folder, '\n']))
    else:
        f.write('\n')
