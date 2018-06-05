import os
import pandas as pd
from pylatex import Document, LongTable, MultiColumn

df = pd.read_csv('data_characteristics.csv',
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
                    subrow[-1] = subrow[-1][:max]
                    data_table.add_row(subrow)
                    while finished is False:
                        last_element = row[-1][max:max + max_classes]
                        subrow = ['', '', '', '', last_element]
                        data_table.add_row(subrow)
                        max = max + max_classes
                        if max >= len(row[-1]):
                            finished = True
                else:
                    data_table.add_row(row)

    doc.generate_pdf("data_characteristics", clean_tex=True)


genenerate_table()
