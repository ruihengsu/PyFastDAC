import itertools

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

time = np.linspace(0,100,100)
def data_gen():
    for i in range(100):
        yield i, np.sin(2*np.pi*time[i]) * np.exp(-time[i]/10.) +100

def init():
    ax.set_ylim(-1.1, 1.1)
    ax.set_xlim(0, 10)
    del xdata[:]
    del ydata[:]
    line.set_data(xdata, ydata)
    return line,

fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)
ax.grid()
xdata, ydata = [], []


def run(data):
    # update the data
    i, y = data
    xdata.append(time[i])
    ydata.append(y)
    xmin, xmax = ax.get_xlim()
    print(i)
    if i in [20,30,40,50]:
        ax.set_ylim(min(ydata), max(ydata))
        
        ax.figure.canvas.draw()
    line.set_data(xdata, ydata)

    return line,

ani = animation.FuncAnimation(fig, run, data_gen, interval=10, init_func=init, blit=True)
plt.show()