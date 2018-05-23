import os
import shutil
import pandas as pd
import numpy as np
import warnings
import math
import os
from sklearn.model_selection import StratifiedKFold


# Ignore warnings
def warn(*args, **kwargs):
    pass


warnings.warn = warn

# # MERGING TRAINING AND SETS DATASETS .1 IN ONE FILE
data_folder = 'data'
processed_folder = 'processed/'
log = 'logs/kfold_error.txt'

if not os.path.isdir(data_folder):
    os.mkdir(data_folder)


def creating_nested_folders():
    # Saving the dataframe into nested folder
    for file in os.listdir(processed_folder):
        if '.data' in file:
            src_folder = os.path.join(processed_folder, file)
            folder_name = file.replace('.data', '')
            end_folder = os.path.join(data_folder, folder_name)
            if os.path.isdir(end_folder):
                shutil.rmtree(end_folder)
            os.mkdir(end_folder)
            shutil.copy(src_folder, end_folder)


def dir_file(file=None):
    dir_file_pairs = list()

    if file is None:
        listdir = os.listdir(data_folder)
    else:
        listdir = [line.replace('.data\n', '').replace('processed/', '') for line in open(file, 'r')]

    for dir_name in listdir:
        full_dir_name = os.path.join(data_folder, dir_name)
        for file_name in os.listdir(full_dir_name):
            if '.data' == file_name[-5:]:  # Storing data name
                dir_file_pairs.append((full_dir_name, file_name))
            else:
                file_to_delete = os.path.join(full_dir_name, file_name)
                os.remove(file_to_delete)

    return dir_file_pairs


def k_folding(file=None):
    dir_file_pairs = dir_file(file)

    # SPLITTING ONE DATASET FILE IN N_FOLDS
    n_fold = 10
    with open(log, 'w') as f:
        for dir_file_pair in dir_file_pairs:
            try:
                dir_name, file_name = dir_file_pair
                df_file = pd.read_csv(os.path.join(dir_name, file_name),
                                      sep='\s+',
                                      header=None)
                target_position = df_file.columns[-1]
                x = df_file[[i for i in range(target_position)]]
                y = df_file[[target_position]]
                # Testing if there is enough instances for n fold
                count = [np.count_nonzero(y == label) for label in np.unique(y)]
                rep = np.max(count)  # If maximum is not enough to n fold
                if n_fold > rep:
                    times = math.ceil(n_fold / rep)
                    x = pd.concat(times * [x])
                    y = pd.concat(times * [y])
                # Shuffle false in order to preserve
                i = 0
                file = file_name.replace('.data', '')
                skf = StratifiedKFold(n_splits=n_fold, shuffle=False)
                for train_index, test_index in skf.split(X=x, y=y):
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
                print('{} can\'t be stratified'.format(file_name))
                f.write(os.path.join('processed/', file_name))
                f.write('\n')
                shutil.rmtree(dir_name)


if __name__ == '__main__':
    print('Creating nested folders...')
    creating_nested_folders()
    print('K folding the datasets...')
    print()
    k_folding()
    # k_folding(file=log)
