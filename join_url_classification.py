import configparser
import os

folder_classification = 'datafiles/classification/'
dataset_folders = list()
list_files = list()

for folder in os.listdir(folder_classification):
    complete_folder = ''.join([folder_classification, folder])
    if os.path.isdir(complete_folder):  # It could be a .csv
        dataset_folders.append(folder)
        files = os.listdir(complete_folder)
        for file in files:
            if '.ini' in file:  # It's the config file we're looking for
                list_files.append('/'.join([complete_folder, file]))

with open('database/wget_database.txt', 'w') as f:
    for file in list_files:
        config = configparser.ConfigParser()
        config.read(file)
        try:
            data_url = config['info']['data_url']
            f.write(''.join([data_url, '\n']))
        except Exception as e:
            print(e)
