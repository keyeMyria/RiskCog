import os
import numpy as np
import matplotlib.pyplot as plt
import sys

if __name__ == '__main__':
    path = sys.argv[1]
    axis = sys.argv[2]

    raw_data = np.loadtxt(path).reshape(-1, 9)

    plt.figure()
    for i in range(9):
        plt.subplot(331+i)
        print raw_data[:, i]
        plt.plot(raw_data[:, i])
    plt.show()
    plt.close()
