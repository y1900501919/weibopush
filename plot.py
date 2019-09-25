import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import math

def plot_polyline(x_names, values, save_path):
    plt.plot(x_names, values)
    plt.yticks(range(min(values), math.ceil(max(values))+1))
    plt.savefig(save_path)
    plt.clf()
    return save_path
