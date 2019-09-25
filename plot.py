import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import math

def plot_polyline(title, x_names, values, save_path):
    plt.title(title)
    plt.plot(x_names, values)
    plt.yticks(range(min(values), math.ceil(max(values))+1))
    plt.savefig(save_path)
    return save_path