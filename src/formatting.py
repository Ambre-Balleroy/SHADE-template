import collections
import pandas as pd
import numpy as np

def discrete_to_continuous(df):
    data = collections.defaultdict(list)
    for freqs in df["frequency"].unique():
        if "-" in freqs:
            freqs_range = range(
                int(freqs.split("-")[0]), int(freqs.split("-")[1]) + 1, 10
            )
            for freq_value in freqs_range:
                data["frequency"].append(freq_value)
                data["level (dB)"].append(
                    df.loc[df["frequency"] == freqs]["Mean"].values[0]
                )
                data["err"].append(
                    df.loc[df["frequency"] == freqs]["SD+1_format"].values[0]
                )
        else:
            data["frequency"].append(int(freqs))
            data["level (dB)"].append(
                df.loc[df["frequency"] == freqs]["Mean"].values[0]
            )
            data["err"].append(
                df.loc[df["frequency"] == freqs]["SD+1_format"].values[0]
            )
    df_formatted = pd.DataFrame(data)
    return df_formatted


def read_automeris_output(csv_file):
    df =  pd.read_csv(
        csv_file,
        sep=";",
        decimal=",",
        names=["frequency", "level", "tuple_id", "type"],
        converters={"type": str.strip},
    )
    df = df.replace(r'^\s*$', np.nan, regex=True)
    return df

def read_multiindex_from_automeris(file):
    """source: https://stackoverflow.com/questions/30322581/pandas-read-multiindexed-csv-with-blanks"""
    df = pd.read_csv(file, header=[0, 1])
    columns = pd.DataFrame(df.columns.tolist())
    columns.loc[columns[0].str.startswith('Unnamed:'), 0] = np.nan
    columns[0] = columns[0].ffill()
    mask = pd.isnull(columns[0])
    columns[0] = columns[0].fillna('')
    columns.loc[mask, [0,1]] = columns.loc[mask, [1,0]].values
    df.columns = pd.MultiIndex.from_tuples(columns.to_records(index=False).tolist())
    return df

def read_and_format_multiindex(file, x_name, y_name, hue_name):
    df = read_multiindex_from_automeris(file)
    df = df.rename(columns={"X":x_name, "Y":y_name}, level=1)
    df = df.stack(0, future_stack=True).reset_index(level=1).reset_index(drop=True)
    df = df.rename(columns={"level_1":hue_name})
    df = df.sort_values([hue_name, x_name])
    return df


def interpolate_conditions(df:pd.DataFrame, condition_col:str, freq_range, id_col=None):
    """Interpolate all the conditions to the same frequency points. Probably unefficient because of the loop, but the dfs it's intended to work on are small anyway."""
    interp_data = {}
    for condition in df[condition_col].unique():
        sub_df = df.loc[df[condition_col]==condition]
        interp_data[condition] = np.interp(freq_range, sub_df["frequency"], sub_df["level"])
    df_interp = pd.DataFrame(interp_data)
    df_interp["frequency"]=freq_range
    df_interp = df_interp.melt(id_vars="frequency", value_name="level", var_name="condition")
    return df_interp.dropna(subset="level")