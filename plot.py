import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import math
import numpy as np

def plot_polyline(x_names, values, save_path):
    y_pos = np.arange(len(x_names))
    barlist = plt.bar(y_pos, values, align='center', alpha=0.5)
    barlist[-2].set_color('r')
    barlist[-1].set_color('g')
    plt.xticks(y_pos, x_names, rotation=60)
    plt.savefig(save_path)
    plt.clf()
    return save_path
