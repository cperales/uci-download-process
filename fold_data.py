import os
import shutil
import pandas as pd
import numpy as np
import warnings
import math
import os
from sklearn.model_selection import StratifiedKFold, KFold
from download_data import check_folder, remove_folder


# Ignore warnings
def warn(*args, **kwargs):
    pass


warnings.warn = warn


def creating_nested_folders(processed_folder,
                            data_folder):
    # Saving the dataframe into nested folder
    for file in os.listdir(processed_folder):
        if '.data' in file:
            # Data folder
            src_folder = os.path.join(processed_folder, file)
            folder_name = file.replace('.data', '')
            end_folder = os.path.join(data_type_folder, folder_name)
            if os.path.isdir(end_folder):
                shutil.rmtree(end_folder)
            os.mkdir(end_folder)
            shutil.copy(src_folder, end_folder)


def dir_file(data_folder, file=None):
    dir_file_pairs = list()

    if file is None:
        listdir = os.listdir(data_folder)
    else:
        listdir = list()
        for line in open(file, 'r'):
            new_line = line.replace('.data\n', '')
            new_new_line = new_line.replace('processed/', '')
            listdir.append(new_new_line)

    for dir_name in listdir:
        full_dir_name = os.path.join(data_folder, dir_name)
        for file_name in os.listdir(full_dir_name):
            if '.data' == file_name[-5:]:  # Storing data name
                dir_file_pairs.append((full_dir_name, file_name))
            else:
                file_to_delete = os.path.join(full_dir_name, file_name)
                os.remove(file_to_delete)

    return dir_file_pairs


def k_folding(data_folder, log_file, file=None, classification=True):
    dir_file_pairs = dir_file(data_folder, file)

    # SPLITTING ONE DATASET FILE IN N_FOLDS
    n_fold = 10
    with open(log_file, 'w') as f:
        for dir_file_pair in dir_file_pairs:
            try:
                dir_name, file_name = dir_file_pair
                print('K folding', dir_name, '...')
                # print('Folding {}'.format(file_name))
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
                f.write(os.path.join('processed/', file_name))
                f.write('\n')
                shutil.rmtree(dir_name)


if __name__ == '__main__':
    processed_folders = ['processed_data/regression']
    log_file = 'logs/kfold_error.txt'
    data_folder = 'data/'
    check_folder(data_folder)

    for processed_folder in processed_folders:
        # Data  type folder
        data_type = os.path.split(processed_folder)[1]
        if 'classification' in data_type:
            classification = True
        else:
            classification = False
        data_type_folder = os.path.join(data_folder, data_type)
        # Remove and create folder
        remove_folder(data_type_folder)
        check_folder(data_type_folder)

        creating_nested_folders(processed_folder,
                                data_type_folder)
        k_folding(data_type_folder, log_file, classification=classification)
