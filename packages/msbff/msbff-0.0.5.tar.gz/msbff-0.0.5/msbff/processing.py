import numpy as np
import pandas as pd
from msbff.default import RT_COL, MZ_COL, PCC_COL, SN_COL


def calc_pcc_sum(df: pd.DataFrame):
    """calculate the summation of PCC column.

    Args:
        df: Filtered dataframe.

    Returns: Summation of PCC column.

    """
    pcc_sum = df[PCC_COL].sum()
    return pcc_sum


def calc_sn_sum(df: pd.DataFrame):
    """calculate the summation of S/N average column.

    Args:
        df: Filtered dataframe.

    Returns: Summation of S/N average column.

    """
    sn_sum = df[SN_COL].sum()
    return sn_sum


def block(df: pd.DataFrame,
          rt_lower, rt_upper, rt_binning,
          mz_lower, mz_upper, mz_binning):
    n_rt_bins = int((rt_upper - rt_lower) // rt_binning)
    n_mz_bins = int((mz_upper - mz_lower) // mz_binning)

    rt_bins = np.arange(rt_lower, rt_lower + (n_rt_bins + 1) * rt_binning, rt_binning)
    mz_bins = np.arange(mz_lower, mz_lower + (n_mz_bins + 1) * mz_binning, mz_binning)

    groups = df.groupby(by=[pd.cut(df[RT_COL], bins=rt_bins), pd.cut(df[MZ_COL], bins=mz_bins)])
    return groups


def block_score(groups, pcc_sum):
    block_score_df = groups[PCC_COL].sum().to_frame().unstack() / pcc_sum * 100
    return block_score_df


def max_inhibition_rate_per_block(groups):
    max_inhibition_rate_df = groups[PCC_COL].max().to_frame().unstack()
    return max_inhibition_rate_df


def relative_signal_intensity_per_block(groups, sn_sum):
    relative_signal_intensity_df = groups[MZ_COL].sum().to_frame().unstack() / sn_sum * 100
    return relative_signal_intensity_df


def processing_pipeline(df: pd.DataFrame, rt_lower, rt_upper, rt_binning, mz_lower, mz_upper, mz_binning):
    groups = block(df, rt_lower, rt_upper, rt_binning, mz_lower, mz_upper, mz_binning)

    pcc_sum = calc_pcc_sum(df)
    block_score_df = block_score(groups, pcc_sum)

    max_inhibition_rate_df = max_inhibition_rate_per_block(groups)

    sn_sum = calc_sn_sum(df)
    relative_signal_intensity_df = relative_signal_intensity_per_block(groups, sn_sum)

    return block_score_df, max_inhibition_rate_df, relative_signal_intensity_df

#
# if __name__ == '__main__':
#     csv_path = "/Users/zhouzhenyi/Documents/github/SciProc/BioFF/msbff/test/dataextraction.csv"
#     df = pd.read_csv(csv_path)
#     block_score_df, max_inhibition_rate_df, relative_signal_intensity_df = processing_pipeline(df, 1, 100)
#     block_score_df.to_csv("block_score.csv")
#     max_inhibition_rate_df.to_csv("max_inhibition_rate.csv")
#     relative_signal_intensity_df.to_csv("relative_signal_intensity.csv")
