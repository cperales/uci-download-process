import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder

origin_folder = 'database/'
final_folder = 'processed/'

for file in os.listdir(origin_folder):
    try:
        df = pd.read_csv(''.join([origin_folder, file]), sep=',', header=None)
        if df[0].dtype != int and df[0].dtype != float:
            le = LabelEncoder()
            df[0] = le.fit_transform(df[0]) + 1

        for c in df.columns[1:]:
            if df[c].dtype == float or df[c].dtype == int:  # It is a float, but it was parsed as int
                df[c] = pd.Series(df[c], dtype=float)
            else:  # It was a string, need to be transformed
                le = LabelEncoder()
                try:
                    df[c] = pd.Series(le.fit_transform(df[c]) + 1, dtype=float)
                except Exception as e:
                    print(e)

        # Changing label (first column) to last column
        a = df[df.columns[-1]]
        df[df.columns[-1]] = df[0]
        df[0] = a

        # Saving the dataframe
        df.to_csv(''.join([final_folder, file]), sep=' ', header=False, index=False)
    except pd.errors.ParserError:
        print(' '.join([file, 'gives a parser error']))

    except UnicodeDecodeError:
        print(' '.join([file, 'gives an Unicode error']))
