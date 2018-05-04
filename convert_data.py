import os
import configparser
import pandas as pd
from sklearn.preprocessing import LabelEncoder

config_folder = 'datafiles/classification/'
processed_folder = 'processed/'
error_files = list()

if not os.path.isdir(processed_folder):
    os.mkdir(processed_folder)

for directory in os.listdir(config_folder):
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
                # Read data
                df = pd.read_csv('/'.join([full_dir, data_file]), sep=',', header=None)
                # Read config file
                config = configparser.ConfigParser()
                config.read('/'.join([full_dir, config_file]))
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

                # Saving the dataframe
                df.to_csv(''.join([processed_folder, data_file]), sep=' ', header=False, index=False)
            except pd.errors.ParserError:
                print(' '.join([data_file, 'gives a parser error']))
                error_files.append(data_file)

            except UnicodeDecodeError:
                print(' '.join([data_file, 'gives an Unicode error']))
                error_files.append(data_file)

            except KeyError:
                print(' '.join([data_file, 'gives a KeyError']))
                error_files.append(data_file)

            except TypeError:
                print(' '.join([data_file, 'gives a TypeError']))
                error_files.append(data_file)

        else:
            print('{} does not have .data and .ini files'.format(full_dir))
            error_files.append(full_dir)

with open('error_files.txt', 'w') as f:
    for file in error_files:
        f.write(''.join([file, '\n']))
