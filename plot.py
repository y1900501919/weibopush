import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import math
import numpy as np
from utils import date_to_str

def plot_polyline(x_names, values, save_path):
    y_pos = np.arange(len(x_names))
    barlist = plt.bar(y_pos, values, align='center', alpha=0.5)
    today_date = date_to_str(date_format='%m/%d')
    yesterday_date = date_to_str(date_format='%m/%d', days_ago=1)

    if today_date in x_names:
        barlist[x_names.index(today_date)].set_color('g')
    if yesterday_date in x_names:
        barlist[x_names.index(yesterday_date)].set_color('r')

    plt.xticks(y_pos, x_names, rotation=60)
    plt.savefig(save_path)
    plt.clf()
    return save_path
