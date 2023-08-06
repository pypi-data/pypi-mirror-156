import os.path

import matplotlib.pyplot as plt
import numpy as np
from msbff.default import (FIG_A_COLOR, FIG_B_COLOR, FIG_C_COLOR, FIG_D_COLOR,
                           FIG_A_XLABEL, FIG_A_YLABEL, FIG_BCD_XLABEL, FIG_BCD_YLABEL,
                           FIG_B_CBAR_TITILE, FIG_C_CBAR_TITILE, FIG_D_CBAR_TITILE,
                           NUMBER_TITLE_FONTDICT, LABEL_FONTDICT, M3_FIG_NAME)

# # test import (待删)
# from preprocessing import read_rawdata
# import pandas as pd
# from processing import processing_pipeline


# # test import (待删)

def set_layout():
    fig = plt.figure(figsize=(16, 12))  # 16 * 12

    ax1 = fig.add_axes([0.1, 0.55, 0.3, 0.3])
    ax2 = fig.add_axes([0.45, 0.55, 0.3, 0.3])
    ax3 = fig.add_axes([0.1, 0.15, 0.3, 0.3])
    ax4 = fig.add_axes([0.45, 0.15, 0.3, 0.3])
    ax5 = fig.add_axes([0.82, 0.65, 0.015, 0.13])
    ax6 = fig.add_axes([0.82, 0.45, 0.015, 0.13])
    ax7 = fig.add_axes([0.82, 0.25, 0.015, 0.13])
    axs = [ax1, ax2, ax3, ax4, ax5, ax6, ax7]
    return fig, axs


def heatmap(data, row_labels, col_labels, x_label, y_label,
            ax, title, labelright=True, **kwargs):
    # Plot the heatmap
    im = ax.imshow(data, **kwargs)
    ax.yaxis.tick_right()

    # Show all ticks and label them with the respective list entries.
    ax.set_xticks(np.arange(data.shape[1]), labels=col_labels, rotation=45)
    ax.set_yticks(np.arange(data.shape[0]), labels=row_labels)

    ax.set_xlabel(x_label, fontdict=LABEL_FONTDICT)
    ax.set_ylabel(y_label, fontdict=LABEL_FONTDICT)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=False, bottom=False, left=False, right=False,
                   labelbottom=True, labelright=labelright)

    # Create white grid.
    ax.set_xticks(np.arange(data.shape[1] + 1) - .5, minor=True)
    ax.set_yticks(np.arange(data.shape[0] + 1) - .5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, right=False)

    # Set title.
    ax.set_title(title, fontdict=NUMBER_TITLE_FONTDICT, position=[-0.15, 0])

    return im


def add_colorbar(fig, im, cax, title):
    cb = fig.colorbar(im, cax=cax)
    cb.ax.set_title(title, loc="left", fontsize=10, weight='bold')
    cb.ax.tick_params(labelsize=10, direction='in')
    return cb


def line_chart(x, y, x_label, y_label, color, ax, title):
    im = ax.plot(x, y, 'o-', color=color)
    ax.set_xlabel(x_label, fontdict=LABEL_FONTDICT)
    ax.set_ylabel(y_label, fontdict=LABEL_FONTDICT)
    ax.set_title(title, fontdict=NUMBER_TITLE_FONTDICT, position=[-0.15, 0])
    return im


def preproc_max_inhibition_rate_df(max_inhibition_rate_df):
    max_value = max_inhibition_rate_df.max().max()
    if float(max_value) > 0.1:
        min_value = max_value - 0.1
        return max_inhibition_rate_df[max_inhibition_rate_df > min_value]
    else:
        return max_inhibition_rate_df


def plot_pipeline(bioactivity_df, block_score_df, max_inhibition_rate_df, relative_signal_intensity_df, output_folder):
    plt.rcParams['font.sans-serif'] = ['Times New Roman']
    plt.rcParams['font.weight'] = "bold"
    fig, axs = set_layout()

    im1 = line_chart(x=bioactivity_df.index, y=bioactivity_df.values,
                     x_label=FIG_A_XLABEL, y_label=FIG_A_YLABEL,
                     color=FIG_A_COLOR, ax=axs[0], title="A")

    im2 = heatmap(block_score_df.values.T,
                  row_labels=block_score_df.columns.get_level_values(1), col_labels=block_score_df.index,
                  x_label=FIG_BCD_XLABEL, y_label=FIG_BCD_YLABEL,
                  ax=axs[1], title="B", cmap=FIG_B_COLOR)

    max_inhibition_rate_df = preproc_max_inhibition_rate_df(max_inhibition_rate_df)
    im3 = heatmap(max_inhibition_rate_df.values.T,
                  row_labels=max_inhibition_rate_df.columns.get_level_values(1),
                  col_labels=max_inhibition_rate_df.index,
                  x_label=FIG_BCD_XLABEL, y_label=FIG_BCD_YLABEL, labelright=False,
                  ax=axs[2], title="C", cmap=FIG_C_COLOR)

    im4 = heatmap(relative_signal_intensity_df.values.T,
                  row_labels=relative_signal_intensity_df.columns.get_level_values(1),
                  col_labels=relative_signal_intensity_df.index,
                  x_label=FIG_BCD_XLABEL, y_label=FIG_BCD_YLABEL,
                  ax=axs[3], title="D", cmap=FIG_D_COLOR)

    add_colorbar(fig, im2, cax=axs[4], title=FIG_B_CBAR_TITILE)
    add_colorbar(fig, im3, cax=axs[5], title=FIG_C_CBAR_TITILE)
    add_colorbar(fig, im4, cax=axs[6], title=FIG_D_CBAR_TITILE)

    plt.savefig(os.path.join(output_folder, M3_FIG_NAME), dpi=300)

    # plt.show()


# if __name__ == '__main__':
#     fp = "/Users/zhouzhenyi/Documents/github/SciProc/MSBFF/msbff/test/rawdata.csv"
#     _, _, _, bioactivity_df = read_rawdata(fp)
#
#     csv_path = "/Users/zhouzhenyi/Documents/github/SciProc/MSBFF/msbff/test/dataextraction.csv"
#     df = pd.read_csv(csv_path)
#
#     block_score_df, max_inhibition_rate_df, relative_signal_intensity_df = processing_pipeline(df, 0, 8, 1, 0, 800, 100)
#     # print(block_score_df.columns.get_level_values(1))
#     plot_pipeline(bioactivity_df, block_score_df, preproc_max_inhibition_rate_df(max_inhibition_rate_df),
#                   relative_signal_intensity_df, ".")
