import pandas as pd
from msbff.default import TARGET_COLUMNS, PCC_COL, RELI_COL, FDR_COL, MZ_COL, SN_COL, RT_COL, CLASS, BIOACTIVITY


def read_rawdata(csv_file: str) -> (pd.DataFrame, pd.DataFrame, pd.Series):
    """Read the raw data and get the target content.

    Args:
        csv_file: Raw data in csv format.

    Returns: Three pieces of data content for subsequent processing.
    """
    class_bioactivity = pd.read_csv(csv_file, nrows=1).dropna(axis=1).set_index(keys=[CLASS]).loc[BIOACTIVITY]
    bioactivity_objective = class_bioactivity.copy()
    main_df = pd.read_csv(csv_file, header=3)
    target_df = main_df[TARGET_COLUMNS]
    bioactivity_df = main_df.iloc[:, -len(bioactivity_objective):]
    bioactivity_objective.index = bioactivity_df.columns
    return target_df, bioactivity_df, bioactivity_objective, class_bioactivity


def calc_pcc(df: pd.DataFrame, objective: pd.Series) -> pd.Series:
    """Calculate the Pearson correlation coefficient for the Bioactivity term.

    Args:
        df: Dataframe of bioactivity data.
        objective: Objective item for bioactivity data.

    Returns: A Series of pairwise correlations.
    """
    pcc = df.corrwith(other=objective, method="pearson", axis=1)
    pcc.name = PCC_COL
    return pcc


def calc_reli(df: pd.DataFrame) -> pd.Series:
    """Calculate the Reliability for the Bioactivity term.

    Args:
        df: Dataframe of bioactivity data.

    Returns: A Series of pairwise reliability.
    """
    reli = 1 - (df == 0).astype(int).sum(axis=1) / len(df.columns)
    reli.name = RELI_COL
    return reli


def filter_data(df: pd.DataFrame,
                pcc_threshold: float,
                reli_threshold: float,
                mz_lower: float,
                mz_upper: float,
                sn_threshold: float,
                rt_lower: float,
                rt_upper: float
                ) -> pd.DataFrame:
    """Filter data according to limited requirements.

    Args:
        df: Data to be filtered.
        pcc_threshold: Pearson correlation coefficient threshold.
        reli_threshold: Reliability threshold.
        mz_lower: Lower limit of the average Mz.
        mz_upper: Upper limit of the average Mz.
        sn_threshold: S/N average threshold.
        rt_lower: Lower limit of the Average Rt(min).
        rt_upper: Upper limit of the Average Rt(min).

    Returns: Filtered data.
    """

    pcc_condition = (df[PCC_COL] > pcc_threshold)
    reli_condition = (df[RELI_COL] >= reli_threshold)
    mz_condition = (mz_lower < df[MZ_COL]) & (df[MZ_COL] <= mz_upper)
    sn_condition = (df[SN_COL] > sn_threshold)
    rt_condition = (rt_lower < df[RT_COL]) & (df[RT_COL] <= rt_upper)

    filtered_df = df[pcc_condition & reli_condition & mz_condition & sn_condition & rt_condition]
    return filtered_df


def calc_fdr(df: pd.DataFrame) -> pd.Series:
    """Calculate FDR for the data.

    Args:
        df: A dataframe sorted by PCC.

    Returns: A Series of FDR.

    """
    fdr = pd.Series((df.index + 1) / len(df), name=FDR_COL)
    return fdr


def fdr_filter(df: pd.DataFrame, fdr_threshold: float) -> pd.DataFrame:
    """Filter data according to FDR.

    Args:
        df: Data to be filtered.
        fdr_threshold: FDR threshold.

    Returns: Filtered data.

    """
    fdr_condition = (df[FDR_COL] >= fdr_threshold)
    filtered_df = df[fdr_condition]
    return filtered_df


def preprocessing_pipeline(csv_file: str,
                           pcc_threshold: float,
                           reli_threshold: float,
                           mz_lower: float,
                           mz_upper: float,
                           sn_threshold: float,
                           rt_lower: float,
                           rt_upper: float,
                           fdr_threshold: float
                           ):
    target_df, bioactivity_df, bioactivity_objective, class_bioactivity = read_rawdata(csv_file)
    pcc = calc_pcc(bioactivity_df, bioactivity_objective)
    reli = calc_reli(bioactivity_df)
    concat_df = pd.concat([target_df, pcc, reli], axis=1)
    filtered_df = filter_data(concat_df,
                              pcc_threshold,
                              reli_threshold,
                              mz_lower,
                              mz_upper,
                              sn_threshold,
                              rt_lower,
                              rt_upper)
    sorted_df = filtered_df.sort_values(by=[PCC_COL], ignore_index=True)
    fdr = calc_fdr(sorted_df)
    fdr_concat_df = pd.concat([sorted_df, fdr], axis=1)
    fdr_filtered_df = fdr_filter(fdr_concat_df, fdr_threshold)
    return fdr_filtered_df, class_bioactivity


# if __name__ == '__main__':
#     fp = "/Users/zhouzhenyi/Documents/github/SciProc/BioFF/msbff/test/rawdata.csv"
#     # preprocessing_pipeline(fp, 0, 0.4, 100, 700, 100, 0, 7, 0.05).to_csv("dataextraction.csv", index=False)
#     _, _, _, df = read_rawdata(fp)
#     print(df)
