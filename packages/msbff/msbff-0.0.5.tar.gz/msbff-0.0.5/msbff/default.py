# names in input table
CLASS = "Class"
BIOACTIVITY = "Bioactivity"

RT_COL = "Average Rt(min)"
MZ_COL = "Average Mz"
SN_COL = "S/N average"
PCC_COL = "PCC"
RELI_COL = "Reliability"
FDR_COL = "FDR"

TARGET_COLUMNS = [RT_COL, MZ_COL, SN_COL]

# output file names
M1_OUTPUT_FILENAME = "data_extraction.csv"
M2_BLOCK_SCORE = "block_score.csv"
M2_MAX_INHIBITION_RATE = "max_inhibition_rate.csv"
M2_RELATIVE_SIGNAL_INTENSITY = "relative_signal_intensity.csv"
M3_FIG_NAME = "Fig.png"

# plot config
FIG_A_COLOR = "purple"
FIG_B_COLOR = "Blues"
FIG_C_COLOR = "Reds"
FIG_D_COLOR = "Greens"

FIG_A_XLABEL = "Class"
FIG_A_YLABEL = "Bioactivity"

FIG_BCD_XLABEL = "Retention Time (min)"
FIG_BCD_YLABEL = "Molecular Weight (Da)"

FIG_B_CBAR_TITILE = "Block Score"
FIG_C_CBAR_TITILE = "Maximum Inhibition Rate Per Block"
FIG_D_CBAR_TITILE = "Relative Signal Intensity Per Block"

NUMBER_TITLE_FONTDICT = {"fontsize": 28, "weight": 'bold'}
LABEL_FONTDICT = {"fontsize": 16}
