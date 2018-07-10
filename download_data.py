import configparser
import os
import shutil
import subprocess


def download_files(config_folder,
                   log_file,
                   raw_data_folder):
    dataset_folders = list()
    list_files = list()

    with open(log_file, 'w') as f:
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
                            final_filename = os.path.join(complete_folder, data_name)
                            # Download file
                            bash_command = ['wget', '-nc', data_url, '-O', final_filename]
                            subprocess.run(bash_command)
                            # Copy file to raw data folder
                            final_filename_2 = os.path.join(raw_data_folder, data_name)
                            shutil.copyfile(final_filename, final_filename_2)
                        except Exception as e:
                            print(e)


def remove_files(config_folder):
    """
    Remove files from configuration folders.
    """
    for folder in os.listdir(config_folder):
        complete_folder = os.path.join(config_folder, folder)
        if os.path.isdir(complete_folder):  # It could be a .csv
            files = os.listdir(complete_folder)
            for file in files:
                if '.ini' not in file:
                    os.remove(os.path.join(complete_folder, file))


if __name__ == '__main__':
    config_folder = 'datafiles/classification/'
    log_file = 'logs/classification_db.txt'
    raw_data_folder = 'raw_data'

    for folder in config_folder, raw_data_folder:
        if not os.path.isdir(folder):
            os.mkdir(folder)

    # remove_files(config_folder)

    download_files(config_folder,
                   log_file,
                   raw_data_folder)
