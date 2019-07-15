import configparser
import os
import shutil
import subprocess


def download_files(config_folder,
                   raw_data_folder,
                   log_file):
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


def check_folder(folder):
    """
    Create folder is necessary.

    :param str folder:
    """
    if not os.path.isdir(folder):
        os.mkdir(folder)


def remove_folder(folder):
    """
    Remove folder if it exists.

    :param str folder:
    """
    if os.path.isdir(folder):
        shutil.rmtree(folder, ignore_errors=True)


if __name__ == '__main__':
    # config_folders = ['datafiles/classification/', 'datafiles/regression/']
    config_folders = ['datafiles/regression/']
    log_file = 'logs/db.txt'
    raw_data_folder = 'raw_data'

    # Remove and create folder, for a fresh raw data
    remove_folder(raw_data_folder)
    check_folder(raw_data_folder)

    for config_folder in config_folders:
        data_type = config_folder.split('/')[1]
        raw_folder = os.path.join(raw_data_folder, data_type)
        check_folder(raw_folder)

        # remove_files(config_folder)
        download_files(config_folder=config_folder,
                       raw_data_folder=raw_folder,
                       log_file=log_file)
