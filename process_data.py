import os
import re
import shutil
import configparser
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, LabelBinarizer
from download_data import check_folder, remove_folder

separators = {'comma': ',',
              '': r'\s+',
              ';': ';'}

missing = ['?', '-', '*', '']


def process_data(config_folder,
                 processed_folder,
                 log_process,
                 log_download):
    """

    :param str log_process:
    :param str log_download:
    :param str config_folder:
    :param str processed_folder:
    :return:
    """
    # Lists for possible errors
    error_files = list()
    download_error = list()

    # Remove and create processed folder
    if os.path.isdir(processed_folder):
        shutil.rmtree(processed_folder)
    os.mkdir(processed_folder)

    # Folders from configuration
    folders = os.listdir(config_folder)

    # Scroll through folders
    for directory in folders:
        config_file = None
        data_file = None
        full_dir = os.path.join(config_folder, directory)
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
                    with open('/'.join([full_dir, config_file]), 'r', encoding='utf-8') as f:
                        config.read_file(f)
                    # config.read('/'.join([full_dir, config_file]))
                    sep = separators[config['info']['separator']]
                    # Does it have header?
                    header = config['info']['header_lines']
                    if header == '':
                        header = None
                        skiprows = None
                    else:
                        skiprows = int(header)
                        header = int(header) - 1
                        if header < 0:
                            header = None
                    # Does it have index?
                    index = config['info']['id_indices']
                    if index == '':  # There is no index
                        index_col = None
                    else:  # It could be one or several indexes
                        index = eval(index)
                        if isinstance(index, int):  # Just one index
                            index_col = index - 1
                        else:  # Several indexes
                            index_col = list()
                            for i in index:
                                index_col.append(i - 1)
                    # Read data
                    try:
                        df = pd.read_csv('/'.join([full_dir, data_file]),
                                         sep=sep,
                                         index_col=index_col,
                                         # header=header,
                                         header=None,
                                         skiprows=skiprows)
                    except IndexError:  # In some datasets, last column ins class.|index
                        df = pd.read_csv('/'.join([full_dir, data_file]),
                                         sep=sep,
                                         # header=header,
                                         header=None,
                                         skiprows=skiprows)
                        df[df.columns[-1]] = pd.Series([e.split('.|')[0] for e in df[df.columns[-1]]])
                        df[df.columns[-1]] = pd.Series([e.split('[')[0] for e in df[df.columns[-1]]])
                    except pd.errors.ParserError as e:
                        # Maybe there is a easier way
                        sk = int(re.findall(r'\d+', re.findall(r'line \d+', str(e))[0])[0]) - 1
                        df = pd.read_csv('/'.join([full_dir, data_file]),
                                         sep=sep,
                                         index_col=index_col,
                                         # header=header,
                                         header=None,
                                         skiprows=[skiprows, sk])
                    except UnicodeDecodeError as e:
                        df = pd.read_csv('/'.join([full_dir, data_file]),
                                         sep=sep,
                                         index_col=index_col,
                                         # header=header,
                                         header=None,
                                         skiprows=skiprows,
                                         encoding='utf-16le')
                    # Changing label to last column
                    final_column = df.columns[-1]
                    label_column = int(config['info']['target_index']) - 1  # In python, index begins at 0
                    if label_column != final_column:
                        if label_column not in df.columns:
                            raise KeyError('Label index {} is not in columns {}'.format(label_column, df.columns))
                        a = df[final_column].copy()
                        df[final_column] = df[label_column].copy()
                        df[label_column] = a

                    # Now, final column is the column for the label
                    if df[final_column].dtype != int and df[final_column].dtype != float:
                        le = LabelEncoder()
                        try:
                            df[final_column] = le.fit_transform(df[final_column])
                        except TypeError as e:
                            df[final_column] = df[final_column].factorize()[0]

                    if 'regression' in config_folder:
                        df[final_column] = pd.Series(df[final_column],
                                                     dtype=np.float)
                    else:
                        df[final_column] = pd.Series(df[final_column] +
                                                     (1 - np.min(df[final_column].values)),
                                                     dtype=np.int)
                    # Replacing missing by NaN
                    for m in missing:
                        df = df.replace(m, np.nan)

                    # Removing depending on how many data are left out
                    n_len = len(df.index)  # Length of instances
                    m_len = len(df.columns)  # Length of features
                    n_len_rm_rows = len(df.dropna(axis=0).index)  # Length of instances when rows are removed
                    m_len_rm_rows = len(df.dropna(axis=0).columns)  # Length of features when columns are removed
                    n_len_rm_cols = len(df.dropna(axis=1).index)  # Length of instances when columns are removed
                    m_len_rm_cols = len(df.dropna(axis=1).columns)  # Length of features when columns are removed
                    if (n_len_rm_cols > (2 * n_len_rm_rows) and (2 * m_len_rm_cols) > m_len) or n_len_rm_rows == 0:
                        df = df.dropna(axis=1)
                    else:
                        df = df.dropna(axis=0)

                    if len(np.unique(df[final_column])) == 1:
                        # Dropping NaN leaves just one class
                        continue

                    # Store label column
                    label_column = df[final_column].copy()
                    df = df.drop(columns=final_column)
                    columnas = list(df.columns.copy())
                    categoric_indices = config['info']['categoric_indices'].split(',')

                    for c in columnas:
                        series_values = df[c].values
                        i = str(int(c) + 1)
                        try:
                            if i in categoric_indices:
                                raise ValueError
                            # In case it is not pointed in config.ini
                            series = [float(series_values[i])
                                      for i in range(len(df[c]))]
                            df[c] = pd.Series(df[c], dtype=np.float)
                        except ValueError:  # It was a string, need to be transformed
                            number_cat = len(np.unique(series_values))
                            df = df.drop(columns=c)
                            if number_cat == 1:  # It is unuseful
                                pass
                            elif number_cat == 2:
                                df[c] = LabelEncoder().fit_transform(series_values)
                            else:
                                try:
                                    series_binarized = LabelBinarizer().fit_transform(series_values)
                                except ValueError:
                                    raise
                                series_binarized_t = series_binarized.transpose()
                                for i in range(1, number_cat + 1):
                                    c_label = '_'.join([str(c), str(i)])
                                    df[c_label] = series_binarized_t[i - 1]

                    # Restore label column. With this label, we assure this is at the end
                    df['Target'] = label_column

                    # Saving the dataframe into processed folder
                    df.to_csv(os.path.join(processed_folder, data_file), sep=' ', header=False, index=False)

                except pd.errors.ParserError as e:
                    print(' '.join([data_file, 'gives a parser error']))
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
                if config_file is None:
                    if data_file is None:
                        print('{} does not have .data and .ini files'.format(full_dir))
                    else:
                        print('{} does not have .ini file'.format(full_dir))
                else:
                    print('{} does not have .data file'.format(full_dir))
                download_error.append(full_dir)
        else: # This is not a directory
            pass

    log_download_error(log_download=log_download,
                       download_error=download_error)

    log_process_error(log_process=log_process,
                      error_files=error_files)


def log_process_error(log_process, error_files):
    """
    Writhe the errors from processing
    into a log file.

    :param str log_process: Path where the log
        for data process errors is saved.
    :param error_files: List of files with error
    :return:
    """
    with open(log_process, 'w') as f:
        if len(error_files) > 0:
            for file in error_files:
               f.write(''.join([file, '\n']))
        else:
            f.write('\n')


def log_download_error(log_download, download_error):
    """
    Write the errors from downloading into
    a log file.

    :param str log_download: Path where the log
        for data download errors is saved.
    :param download_error: List of files with error
    :return:
    """
    with open(log_download, 'w') as f:
        if len(download_error) > 0:
            for folder in download_error:
                if os.path.isdir(folder):
                    f.write(''.join([folder, '\n']))
        else:
            f.write('\n')


if __name__ == '__main__':
    log_process = 'logs/convert_error.txt'
    log_download = 'logs/download_error.txt'
    # config_folders = ['datafiles/regression', 'datafiles/classification']
    config_folders = ['datafiles/regression']
    processed_data_folder = 'processed_data/'

    # Remove and create folder, for a fresh raw data
    remove_folder(processed_data_folder)
    check_folder(processed_data_folder)

    for config_folder in config_folders:
        data_type = config_folder.split('/')[1]
        processed_folder = os.path.join(processed_data_folder, data_type)
        check_folder(processed_folder)

        process_data(config_folder=config_folder,
                     processed_folder=processed_folder,
                     log_process=log_process,
                     log_download=log_download)
