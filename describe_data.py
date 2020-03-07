import os
import glob
import pandas as pd
import numpy as np
from pylatex import Document, LongTable
from copy import deepcopy
from download_data import check_folder


def description_classification(full_data_files, description_folder):
    description_folder = os.path.join(description_folder, 'classification')
    check_folder(description_folder)
    data_list = list()
    for d in full_data_files:
        name = d.split('/')[2].split('.')[0]
        df = pd.read_csv(d,
                         sep='\s+',
                         header=None)
        lines, columns = df.shape
        attribute = columns - 1  # Minus one because of target
        last_pos = attribute
        classes = np.unique(df[last_pos])
        n_classes = len(classes)
        distribution_list = [len(df[df[last_pos] == c]) for c in classes]
        distribution_list.sort(reverse=True)
        distribution = tuple(distribution_list)
        data_list.append({'Dataset': name,
                          'Size': lines,
                          'Attributes': attribute,
                          'Classes': n_classes,
                          'Class distribution': distribution})

    df = pd.DataFrame(data_list)
    df = df.sort_values('Size', ascending=False)
    cols = ['Dataset',
            'Size',
            'Attributes',
            'Classes',
            'Class distribution']
    df = df[cols]
    df_copy = deepcopy(df)
    df_copy['Class distribution'] = [str(value).replace(', ', ';').replace(')', '').replace('(', '')
                                     for value in df_copy['Class distribution']]
    df_copy.to_csv(os.path.join(description_folder,
                                'data_description.csv'),
                   sep=',',
                   header=True,
                   columns=['Dataset',
                            'Size',
                            'Attributes',
                            'Classes',
                            'Class distribution'],
                   index=False)

    # # LaTeX
    df = df.set_index(['Dataset'])

    # Max classes per row
    max_classes = np.inf
    geometry_options = {
        "margin": "1.00cm",
        "includeheadfoot": True
    }
    doc = Document(page_numbers=True, geometry_options=geometry_options)

    # Generate data table
    with doc.create(LongTable("l l l l l")) as data_table:
            data_table.add_hline()
            header = ["Dataset",
                      "Size",
                      "#Attr.",
                      "#Classes",
                      "Class distribution"]
            data_table.add_row(header)
            data_table.add_hline()
            data_table.add_hline()
            for index in df.index.values:
                row = [index] + df.loc[index].values.tolist()
                if len(row[-1]) > max_classes:
                    max = max_classes
                    finished = False
                    subrow = row.copy()
                    # Select subtuple and removing last parenthesis
                    subrow[-1] = str(subrow[-1][:max]).replace(')', ',')
                    data_table.add_row(subrow)
                    while finished is False:
                        last_element = row[-1][max:max + max_classes]
                        if len(last_element) == 1:
                            # To string
                            last_element = str(last_element)
                            # Remove first and last parenthesis and comma
                            last_element = last_element[1:-2]
                        else:
                            # To string
                            last_element = str(last_element)
                            # Remove first and last parenthesis
                            last_element = last_element[1:-1]
                        max = max + max_classes
                        if max >= len(row[-1]):
                            finished = True
                            last_element += ')'
                        else:
                            # Remove last parenthesis or comma if len is 1
                            last_element = last_element[:-1]
                        subrow = ['', '', '', '', last_element]
                        data_table.add_row(subrow)

                else:
                    data_table.add_row(row)

    doc.generate_pdf(os.path.join(description_folder,
                                  'data_description'), clean_tex=False)


def description_regression(full_data_files, description_folder):
    description_folder = os.path.join(description_folder, 'regression')
    check_folder(description_folder)
    data_list = list()
    for d in full_data_files:
        name = d.split('/')[2].split('.')[0]
        df = pd.read_csv(d,
                         sep='\s+',
                         header=None)
        lines, columns = df.shape
        attribute = columns - 1  # Minus one because of target
        data_list.append({'Dataset': name,
                          'Size': lines,
                          'Attributes': attribute})

    df = pd.DataFrame(data_list)
    df = df.sort_values('Size', ascending=False)
    cols = ['Dataset',
            'Size',
            'Attributes']
    df = df[cols]
    df_copy = deepcopy(df)
    df_copy.to_csv(os.path.join(description_folder,
                                'data_description.csv'),
                   sep=',',
                   header=True,
                   columns=['Dataset',
                            'Size',
                            'Attributes'],
                   index=False)

    # # LaTeX
    df = df.set_index(['Dataset'])

    # Max classes per row
    max_classes = np.inf
    geometry_options = {
        "margin": "1.00cm",
        "includeheadfoot": True
    }
    doc = Document(page_numbers=True, geometry_options=geometry_options)

    # Generate data table
    with doc.create(LongTable("l l l")) as data_table:
            data_table.add_hline()
            header = ["Dataset",
                      "Size",
                      "#Attr."]
            data_table.add_row(header)
            data_table.add_hline()
            data_table.add_hline()
            for index in df.index.values:
                row = [index] + df.loc[index].values.tolist()
                data_table.add_row(row)

    doc.generate_pdf(os.path.join(description_folder,
                                  'data_description'), clean_tex=False)


if __name__ == '__main__':
    description_folder = 'description'
    check_folder(description_folder)

    data_folders = ['data/classification', 'data/regression']
    for data_folder in data_folders:
        full_data_files = glob.glob(data_folder + '/*/*.data')
        if len(full_data_files) >= 1:
            # data_files = [d.split('/')[2].split('.')[0] for d in full_data_files]
            if 'classification' in data_folder:
                description_classification(full_data_files, description_folder)
            else:
                description_regression(full_data_files, description_folder)
