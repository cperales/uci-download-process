import os
import re
import shutil
import configparser
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, LabelBinarizer
from download_data import check_folder, remove_folder, read_config

separators = {'comma': ',',
              ',': ',',
              ', ': ', ',
              '': r'\s+',
              ' ': r'\s+',
              ';': ';',
              ',|': r'\,|\|',
              ',[': r'\,|\['}

missing = {'?': np.nan,
           '-': np.nan,
           '*': np.nan,
           '': np.nan,
           '#DIV/0!': np.nan}


min_target = 5


def process_data(config_folder,
                 processed_folder):
    """

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

    # Classification or regression
    if 'classification' in config_folder:
        print('Processing classification')
        classification = True
    else:
        print('Processing regression')
        classification = False

    # Scroll through folders
    for directory in folders:
        print('Formatting', directory)
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
                    header = config['info']['header']
                    skiprows = config.get('info', 'skiprows', fallback='')
                    if header == '' or header == '0':
                        header = None
                    else:
                        header = int(header) - 1
                    if skiprows == '' or header == '0':
                        skiprows = None
                    else:
                        skiprows = int(skiprows)
                    # Does it have index?
                    index = config['info']['id_indices']
                    if index == '':  # There is no index
                        index_col = None
                    else:  # It could be one or several indexes
                        index_col = [int(i) - 1 for i in index.split(',')]
                        # if isinstance(index, int):  # Just one index
                        #     index_col = index - 1
                        # else:  # Several indexes
                        #     index_col = list()
                        #     for i in index:
                        #         index_col.append(i - 1)

                    # Load only columns needed
                    label_column = int(config['info']['target_index']) - 1  # In python, index begins at 0
                    categoric_indices = config['info']['categoric_indices']
                    if categoric_indices == '':
                        categoric_indices = list()
                    else:
                        categoric_indices = [int(i) - 1 for i in categoric_indices.split(',')]
                    value_indices = config['info']['value_indices']
                    if value_indices == '':
                        value_indices = list()
                    else:
                        value_indices = [int(i) - 1 for i in value_indices.split(',')]
                    indices = categoric_indices + value_indices + [label_column]
                    if index_col is not None:
                        indices += index_col
                    indices = list(set(indices))
                    # Read data
                    try:
                        df = pd.read_csv(os.path.join(full_dir, data_file),
                                         sep=sep,
                                         index_col=index_col,
                                         usecols=indices,
                                         header=None,
                                         skiprows=skiprows,
                                         engine='python')
                    except pd.errors.ParserError as e:
                        # Maybe there is a easier way
                        sk = int(re.findall(r'\d+', re.findall(r'line \d+', str(e))[0])[0]) - 1
                        df = pd.read_csv(os.path.join(full_dir, data_file),
                                         sep=sep,
                                         index_col=index_col,
                                         header=None,
                                         usecols=indices,
                                         skiprows=[skiprows, sk])
                    except UnicodeDecodeError as e:
                        df = pd.read_csv(os.path.join(full_dir, data_file),
                                         sep=sep,
                                         index_col=index_col,
                                         header=None,
                                         skiprows=skiprows,
                                         usecols=indices,
                                         encoding='utf-16le')
                    if header is not None:
                        df = df.iloc[header + 1:]
                    if index_col is not None:
                        # Categoric columns after index reduce the numbers
                        new_categoric_indices = list()
                        for categoric_index in categoric_indices:
                            for main_index in index_col:
                                if categoric_index > main_index:
                                    categoric_index -= 1
                                new_categoric_indices.append(categoric_index)
                        categoric_indices = new_categoric_indices
                        # Value columns after index reduce the numbers
                        new_value_indices = list()
                        for value_index in value_indices:
                            for main_index in index_col:
                                if value_index > main_index:
                                    value_index -= 1
                                new_value_indices.append(value_index)
                        value_indices = new_value_indices
                        for main_index in index_col:
                            if label_column > main_index:
                                label_column -= 1
                    # Renaming columns
                    range_columns = list(set(categoric_indices + value_indices + [label_column]))
                    df.columns = range_columns
                    # # Changing label to last column
                    # final_column = df.columns[-1]
                    # if label_column != final_column:
                    #     if label_column not in df.columns:
                    #         raise KeyError('Label index {} is not in columns {}'.format(label_column, df.columns))
                    #     a = df[final_column].copy()
                    #     df[final_column] = df[label_column].copy()
                    #     df[label_column] = a
                    #     label_column = final_column

                    # Now, final column is the column for the label
                    if classification is True:
                        unique_target, unique_count = np.unique(df[label_column], return_counts=True)
                        if np.min(unique_count) < min_target:
                            raise ValueError('Original data doesn\'t has poor class distribution,', np.min(unique_count))

                    if df[label_column].dtype != int and df[label_column].dtype != float:
                        if 'regression' in config_folder:
                            df[label_column] = pd.Series(df[label_column],
                                                         dtype=np.float32)
                        else:
                            le = LabelEncoder()
                            try:
                                df[label_column] = le.fit_transform([str(e).replace(' ', '')
                                                                     for e in df[label_column]])
                            except TypeError as e:
                                df[label_column] = df[label_column].factorize()[0]
                            df[label_column] = pd.Series(df[label_column] +
                                                         (1 - np.min(df[label_column].values)),
                                                     dtype=np.int32)
                    # Store label column
                    label_series = df[label_column].copy()
                    df = df.drop(columns=label_column)
                    columnas = list(df.columns.copy())
                    if categoric_indices == list():
                        categoric_indices = np.array(categoric_indices)
                    else:
                        categoric_indices = np.array(categoric_indices, dtype=int)

                    # Replacing missing by NaN
                    for c in columnas:
                        if c not in categoric_indices and (df[c].dtype != int and df[c].dtype != float):
                            df[c] = df[c].replace(missing)

                    # Restore label column. With this label, we assure dropna
                    df[label_column] = label_series

                    if pd.isnull(df).values.any() == True:  # Don't work properly with "is"
                        # Removing depending on how many data are left out
                        n_len = len(df.index)  # Length of instances
                        m_len = len(df.columns)  # Length of features
                        # Drop NaN by rows
                        df_dropna_0 = df.dropna(axis=0)
                        # Drop Nan by columns
                        df_dropna_1 = df.dropna(axis=1)
                        if classification is True:
                            if len(df_dropna_0) > 0:
                                _, label_counts_0 = np.unique(df_dropna_0[label_column],
                                                              return_counts=True)
                                if classification is True:
                                    min_label_counts_0 = np.min(label_counts_0)
                            else:
                                min_label_counts_0 = 0
                            _, label_counts_1 = np.unique(df_dropna_1[label_column],
                                                          return_counts=True)
                            min_label_counts_1 = np.min(label_counts_1)
                            if min_label_counts_0 < min_target:
                                if min_label_counts_1 > 5:
                                    df = df_dropna_1
                                else:
                                    raise ValueError(directory, ' omitted. Removing NaNs delete class information')
                            elif min_label_counts_1 < 2:
                                df = df_dropna_0

                        n_len_rm_rows = len(df_dropna_0.index)  # Length of instances when rows are removed
                        m_len_rm_rows = len(df_dropna_0.columns)  # Length of features when columns are removed
                        n_len_rm_cols = len(df_dropna_1.index)  # Length of instances when columns are removed
                        m_len_rm_cols = len(df_dropna_1.columns)  # Length of features when columns are removed
                        if (n_len_rm_cols > (2 * n_len_rm_rows) and (2 * m_len_rm_cols) > m_len) or n_len_rm_rows == 0:
                            df = df_dropna_1
                        else:
                            df = df_dropna_0

                    # Store label column
                    label_series = df[label_column].copy()
                    df = df.drop(columns=label_column)
                    columns = list(df.columns.copy())

                    for c in columns:
                        series_values = df[c].values
                        if c not in categoric_indices:
                            # series = [float(series_values[i])
                            #           for i in range(len(df[c]))]
                            df[c] = pd.Series(df[c], dtype=np.float32)
                        else:  # It was a string, need to be transformed
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
                    df['Target'] = label_series

                    # Saving the dataframe into processed folder
                    df.to_csv(os.path.join(processed_folder, data_file), sep=' ', header=False, index=False)

                except ValueError as e:
                    print(' '.join([data_file, 'gives a ValueError:', str(e)]))
                    error_files.append(data_file)

                except pd.errors.ParserError as e:
                    print(' '.join([data_file, 'gives a parser error:', str(e)]))
                    error_files.append(data_file)

                except KeyError as e:
                    print(' '.join([data_file, 'gives a KeyError:', str(e)]))
                    error_files.append(data_file)

                except TypeError as e:
                    print(' '.join([data_file, 'gives a TypeError:', str(e)]))
                    error_files.append(data_file)

                except IndexError as e:
                    print(' '.join([data_file, 'separator is not correct:', str(e)]))
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
        else:  # This is not a directory
            pass


if __name__ == '__main__':
    try:
        parameter_config = read_config('parameter_config.ini')
    except NameError:
        print('Not custom parameter config file found, using default')
        parameter_config = read_config('default_config.ini')
    config_folders = parameter_config.get('PROCESS',
                                          'config_folders').split(',')

    processed_data_folder = parameter_config.get('PROCESS',
                                                 'processed_folder',
                                                 fallback='processed_data')
    check_folder(processed_data_folder)

    remove_older = eval(parameter_config.get('PROCESS',
                                             'remove_older',
                                             fallback='True'))

    for config_folder in config_folders:
        data_type = config_folder.split('/')[1]
        processed_folder = os.path.join(processed_data_folder, data_type)
        # Remove and create folder
        if remove_older is True:
            remove_folder(processed_folder)
        check_folder(processed_folder)

        process_data(config_folder=config_folder,
                     processed_folder=processed_folder)
        print()
