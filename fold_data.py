import os
import shutil
import pandas as pd
import numpy as np
import warnings
import math
import os
from sklearn.model_selection import StratifiedKFold, KFold
from download_data import check_folder, remove_folder, read_config


# Ignore warnings
def warn(*args, **kwargs):
    pass


warnings.warn = warn


def creating_nested_folders(processed_folder,
                            data_folder):
    # Saving the dataframe into nested folder
    for file in os.listdir(processed_folder):
        # Data folder
        src_folder = os.path.join(processed_folder, file)
        folder_name = file.replace('.data', '')
        end_folder = os.path.join(data_folder, folder_name)
        check_folder(end_folder)
        shutil.copy(src_folder, end_folder)


def dir_file(data_folder):
    dir_file_pairs = [(os.path.join(data_folder, dir_name),
                       '.'.join([dir_name, 'data']))
                       for dir_name in os.listdir(data_folder)]
    return dir_file_pairs


def k_folding(data_folder, n_fold=10):
    # Classification or regression
    if 'classification' in data_folder:
        print('Folding classification')
        classification = True
    else:
        print('Folding regression')
        classification = False
    dir_file_pairs = dir_file(data_folder)

    # SPLITTING ONE DATASET FILE IN N_FOLDS
    for dir_file_pair in dir_file_pairs:
        try:
            dir_name, file_name = dir_file_pair
            print('Folding', file_name[:-5], '...')
            df_file = pd.read_csv(os.path.join(dir_name, file_name),
                                  sep='\s+',
                                  header=None)
            target_position = df_file.columns[-1]
            x = df_file[[i for i in range(target_position)]]
            y = df_file[[target_position]]
            # Shuffle false in order to preserve
            i = 0
            file = file_name.replace('.data', '')
            if classification is True:
                # Testing if there is enough instances for n fold
                count = [np.count_nonzero(y == label) for label in np.unique(y)]
                if np.min(count) < 2:
                    raise ValueError('Not enough elements of one label')
                rep = np.max(count)  # If maximum is not enough to n fold
                if n_fold > rep:
                    times = math.ceil(n_fold / rep)
                    x = pd.concat(times * [x])
                    y = pd.concat(times * [y])
                kf = StratifiedKFold(n_splits=n_fold, shuffle=False)
            else:
                kf = KFold(n_splits=n_fold, shuffle=True)
            for train_index, test_index in kf.split(X=x, y=y):
                x_train_fold = x.iloc[train_index]
                y_train_fold = y.iloc[train_index]
                train_fold = pd.concat([x_train_fold, y_train_fold], axis=1)
                train_fold_name = '.'.join(['_'.join(['train', file]), str(i)])
                train_fold_name_path = os.path.join(dir_name, train_fold_name)
                train_fold.to_csv(train_fold_name_path,
                                  sep=' ',
                                  header=None,
                                  index=False)

                x_test_fold = x.iloc[test_index]
                y_test_fold = y.iloc[test_index]
                test_fold = pd.concat([x_test_fold, y_test_fold], axis=1)
                test_fold_name = '.'.join(['_'.join(['test', file]), str(i)])
                test_fold_name_path = os.path.join(dir_name, test_fold_name)
                test_fold.to_csv(test_fold_name_path,
                                 sep=' ',
                                 header=None,
                                 index=False)

                i += 1
        except ValueError as e:
            print(e, ', '
                     'so {} can\'t be stratified'.format(file_name))
            remove_folder(dir_name)


if __name__ == '__main__':
    try:
        parameter_config = read_config('parameter_config.ini')
    except NameError:
        print('Not custom parameter config file found, using default')
        parameter_config = read_config('default_config.ini')
    processed_folders = parameter_config.get('FOLD',
                                             'processed_folders').split(',')

    fold_data_folder = parameter_config.get('FOLD',
                                       'data_folder',
                                       fallback='data')
    check_folder(fold_data_folder)

    remove_older = eval(parameter_config.get('FOLD',
                                             'remove_older',
                                             fallback='True'))

    n_fold = int(parameter_config.get('FOLD',
                                      'n_fold',
                                      fallback='10'))
    for processed_folder in processed_folders:
        data_type = os.path.split(processed_folder)[1]
        data_folder = os.path.join(fold_data_folder, data_type)
        # Remove and create folder
        if remove_older is True:
            remove_folder(data_folder)
        check_folder(data_folder)

        creating_nested_folders(processed_folder,
                                data_folder)
        k_folding(data_folder=data_folder, n_fold=n_fold)
        print()
