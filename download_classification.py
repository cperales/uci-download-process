import configparser
import os
import wget

config_folder = 'datafiles/classification/'
dataset_folders = list()
list_files = list()
downloaded_data = list()

with open('classification_db.txt', 'w') as f:
    for folder in os.listdir(config_folder):
        complete_folder = ''.join([config_folder, folder])
        if os.path.isdir(complete_folder):  # It could be a .csv
            dataset_folders.append(folder)
            files = os.listdir(complete_folder)
            for file in files:
                if '.ini' in file:  # It's the config file we're looking for
                    config_file = '/'.join([complete_folder, file])
                    list_files.append(config_file)
                    config = configparser.ConfigParser()
                    config.read(config_file)
                    try:
                        data_url = config['info']['data_url']
                        if '.data' in data_url:
                            f.write(''.join([data_url, '\n']))
                            filename = wget.download(data_url, out=complete_folder)
                            downloaded_data.append((filename, config))
                    except Exception as e:
                        print(e)

# import subprocess
# subprocess.run('wget -i classification_db.txt -P database/'.split())