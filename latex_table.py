import os
import pandas as pd
from pylatex import Document, LongTable, MultiColumn

description_folder = 'description'

df = pd.read_csv(os.path.join(description_folder,
                              'data_description.csv'),
                 sep=';',
                 header=0,
                 index_col='Dataset')


def genenerate_table(max_classes=10):
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
                row[-1] = eval(row[-1])
                if len(row[-1]) > 10:
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


genenerate_table()
