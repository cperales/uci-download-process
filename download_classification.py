import configparser
import os
import wget
import pandas as pd
from sklearn.preprocessing import LabelEncoder

config_folder = 'datafiles/classification/'
dataset_folders = list()
list_files = list()

for folder in os.listdir(config_folder):
    complete_folder = ''.join([config_folder, folder])
    if os.path.isdir(complete_folder):  # It could be a .csv
        dataset_folders.append(folder)
        files = os.listdir(complete_folder)
        for file in files:
            if '.ini' in file:  # It's the config file we're looking for
                list_files.append('/'.join([complete_folder, file]))

downloaded_data = list()
with open('classification_db.txt', 'w') as f:
    for file in list_files:
        config = configparser.ConfigParser()
        config.read(file)
        try:
            data_url = config['info']['data_url']
            if '.data' in data_url:
                f.write(''.join([data_url, '\n']))
                filename = wget.download(data_url, out='database/')
                downloaded_data.append((filename, config))
        except Exception as e:
            print(e)

# import subprocess
# subprocess.run('wget -i classification_db.txt -P database/'.split())

db_folder = 'database/'
processed_folder = 'processed/'

for file, config in downloaded_data:
    try:
        df = pd.read_csv(''.join([db_folder, file]), sep=',', header=None)

        # Changing label to last column
        final_column = df.columns[-1]
        label_column = config['info']['target_index']
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
