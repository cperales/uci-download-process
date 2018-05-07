import os
import pandas as pd
from sklearn.model_selection import StratifiedKFold


# # MERGING TRAINING AND SETS DATASETS .1 IN ONE FILE
data_folder = 'uci'

dir_files = []

for dir_name in os.listdir(data_folder):
    full_dir_name = os.path.join(data_folder, dir_name)
    for file_name in os.listdir(full_dir_name):
        if '.data' == file_name[-5:]:  # Storing data name
            dir_files.append((full_dir_name, file_name))
        else:
            file_to_delete = os.path.join(full_dir_name, file_name)
            os.remove(file_to_delete)

# SPLITTING ONE DATASET FILE IN N_FOLDS
n_fold = 10
for pair_dir_file in dir_files:
    try:
        list_df_file = []
        dir_name, file_name = pair_dir_file
        df_file = pd.read_csv(os.path.join(dir_name, file_name),
                              sep='\s+',
                              header=None)
        skf = StratifiedKFold(n_splits=n_fold, shuffle=False)
        target_position = df_file.columns[-1]
        x = df_file[[i for i in range(target_position)]]
        y = df_file[[target_position]]
        # Shuffle false in order to preserve
        i = 0
        file = file_name.replace('.data', '')
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
    except ValueError:
        print('{} can\'t be stratified'.format(pair_dir_file[1]))
