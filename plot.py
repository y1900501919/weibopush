import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import math
import numpy as np
from utils import date_to_str

def plot_status_history(x_names, values, save_path):
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

def plot_stocks(data_lst, save_path):
    plt.title('- TODAY\'S STOCKS -')
    for x_lst, y_lst, legend in data_lst:
        plt.plot(x_lst, y_lst, '-o', label=legend)
        if x_lst and y_lst:
            plt.annotate(y_lst[-1], (x_lst[-1], y_lst[-1]))
    
    plt.xticks(rotation=60)
    plt.legend(loc='upper left')
    plt.savefig(save_path)
    plt.clf()
    return save_path

