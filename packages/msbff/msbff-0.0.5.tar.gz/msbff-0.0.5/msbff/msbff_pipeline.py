import os.path

from msbff.processing import processing_pipeline
from msbff.preprocessing import preprocessing_pipeline
from msbff.visualization import plot_pipeline
from msbff.default import M1_OUTPUT_FILENAME, M2_BLOCK_SCORE, M2_MAX_INHIBITION_RATE, M2_RELATIVE_SIGNAL_INTENSITY
from pathlib import Path


def run_bioff_pipeline(input_csv,
                       output_folder,
                       pcc_threshold,
                       reliability_threshold,
                       mz_lower,
                       mz_upper,
                       sn_threshold,
                       rt_lower,
                       rt_upper,
                       fdr_threshold,
                       rt_binning,
                       mz_binning):
    """Run Bioactive Fractions Filtering Pipeline.

    Args: See the command help information for detailed arguments descriptions.

    Returns: All results will be saved to the specified folder when the program is finished.

    """

    """Check output path."""
    if not Path(output_folder).is_dir():
        raise Exception("Wrong Output Path!")

    """Module1-Preprocessing data: Read data and perform data cleaning."""
    preprocessed_df, class_bioactivity = preprocessing_pipeline(input_csv,
                                                                pcc_threshold,
                                                                reliability_threshold,
                                                                mz_lower,
                                                                mz_upper,
                                                                sn_threshold,
                                                                rt_lower,
                                                                rt_upper,
                                                                fdr_threshold)
    """Save the results of Module1 processing."""
    preprocessed_df.to_csv(os.path.join(output_folder, M1_OUTPUT_FILENAME), index=False)

    """Module2-Processing data: Calculate each variable value."""
    block_score_df, max_inhibition_rate_df, relative_signal_intensity_df = processing_pipeline(preprocessed_df,
                                                                                               rt_lower,
                                                                                               rt_upper,
                                                                                               rt_binning,
                                                                                               mz_lower,
                                                                                               mz_upper,
                                                                                               mz_binning)
    """Save the results of Module2 processing."""
    block_score_df.to_csv(os.path.join(output_folder, M2_BLOCK_SCORE))
    max_inhibition_rate_df.to_csv(os.path.join(output_folder, M2_MAX_INHIBITION_RATE))
    relative_signal_intensity_df.to_csv(os.path.join(output_folder, M2_RELATIVE_SIGNAL_INTENSITY))

    """Module3-Data visualization: Plot one line chart and three heatmap."""
    plot_pipeline(class_bioactivity, block_score_df, max_inhibition_rate_df, relative_signal_intensity_df,
                  output_folder)
