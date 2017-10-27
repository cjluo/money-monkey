import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FormatStrFormatter
from tempfile import NamedTemporaryFile


def plot_to_file(symbol, timestamp, close, score):
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot(timestamp, close, color='r', marker='.', label="close")
    ax2.plot(timestamp, score, color='b', marker='.', label="score")
    plt.title("%s: score %0.2f" % (symbol, score[-1]))

    fig.autofmt_xdate()
    ax1.xaxis.set_major_formatter(DateFormatter("%H:%M"))
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2)

    png_file = NamedTemporaryFile(delete=False, suffix='.png')
    png_file.close()

    fig.set_dpi(100)
    fig.set_size_inches(10, 4)
    fig.set_tight_layout(True)

    fig.savefig(png_file.name)
    plt.close(fig)
    return png_file.name
