import os
import configparser
import pandas as pd
from sklearn.preprocessing import LabelEncoder

db_folder = 'database/'
config_folder = 'datafiles/classification/'
processed_folder = 'processed/'

config_directories = os.listdir(config_folder)

for file in os.listdir(db_folder):
    try:
        df = pd.read_csv(''.join([db_folder, file]), sep=',', header=None)
        config_filename = file.replace('.data', '').lower()
        config_file = '/'.join([''.join([config_folder, config_filename]),
                                'config.ini'])
        if not os.path.isfile(config_file):
            for cd in config_directories:
                if config_filename in cd:
                    config_filename = cd
                    config_file = '/'.join([''.join([config_folder, config_filename]),
                                            'config.ini'])
        config = configparser.ConfigParser()
        config.read(config_file)
        # Changing label to last column
        final_column = df.columns[-1]
        label_column = int(config['info']['target_index'])
        if label_column not in df.columns:
            raise KeyError('Label index {} is not in columns {}'.format(label_column, df.columns))
        a = df[final_column]
        df[final_column] = df[label_column]
        df[label_column] = a

        if df[final_column].dtype != int and df[final_column].dtype != float:
            le = LabelEncoder()
            df[final_column] = le.fit_transform(df[final_column]) + 1

        for c in df.columns[:final_column]:
            if df[c].dtype == float or df[c].dtype == int:  # It is a float, but it was parsed as int
                df[c] = pd.Series(df[c], dtype=float)
            else:  # It was a string, need to be transformed
                le = LabelEncoder()
                try:
                    df[c] = pd.Series(le.fit_transform(df[c]) + 1, dtype=float)
                except Exception as e:
                    print(e)

        # Saving the dataframe
        df.to_csv(''.join([processed_folder, file]), sep=' ', header=False, index=False)
    except pd.errors.ParserError:
        print(' '.join([file, 'gives a parser error']))

    except UnicodeDecodeError:
        print(' '.join([file, 'gives an Unicode error']))

    except KeyError:
        print(' '.join([file, 'gives a KeyError']))
