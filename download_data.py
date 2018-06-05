import configparser
import os
# import wget
import subprocess

config_folder = 'datafiles/classification/'
log = 'logs/classification_db.txt'

if not os.path.isdir('logs'):
    os.mkdir('logs')


def download_files():
    dataset_folders = list()
    list_files = list()

    with open(log, 'w') as f:
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
                            data_name = config['info']['name']
                            f.write(''.join([data_url, '\n']))
                            final_filename = '/'.join([complete_folder, data_name])
                            bash_command = ['wget', '-nc', data_url, '-O', final_filename]
                            subprocess.run(bash_command)
                        except Exception as e:
                            print(e)


def remove_files():
    for folder in os.listdir(config_folder):
        complete_folder = ''.join([config_folder, folder])
        if os.path.isdir(complete_folder):  # It could be a .csv
            files = os.listdir(complete_folder)
            for file in files:
                if '.ini' not in file:
                    os.remove('/'.join([complete_folder, file]))


if __name__ == '__main__':
    download_files()
