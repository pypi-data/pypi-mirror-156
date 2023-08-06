import pandas as pd
import matplotlib.pyplot as plt


def view():
    pd.options.display.float_format = '{:,.2f}'.format  # shows cents!
    return pd.set_option('display.width', None), pd.set_option('display.max_rows', None), \
        pd.set_option('display.max_columns', None), pd.options.display.float_format


def format_cols(df):
    formatted_headers = [x.lower().replace(' ', '_') for x in df.columns]
    return formatted_headers


def label_graph(data, x, y, label):
    for i in data.index:
        record = data.loc[i]
        ax = plt.gca()
        ax.text(record[x] * 1.02, record[y], record[label], size='x-small')
