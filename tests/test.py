import glob
import os
from src.formatting import read_automeris_output # todo: setup this

### tests
def test_tar_project_file(csv_file, tar_folder):
    tar_file = glob.glob(os.path.join(tar_folder, ("_".join(os.path.basename(csv_file).split("_")[:2]).removesuffix(".csv") + "_fig*" + ".tar")))
    assert tar_file != [], (
        f"There is no project tar file associated with {os.path.basename(csv_file)} or it is not named properly"
    )
   


def test_negative_values(df):
    if df["frequency"].dtypes is int:
        assert not (df["frequency"] < 0).values.any(), (
            "No frequency value should be negative"
        )


def test_sorted_values(csv_file, df):
    if not df["type"].isnull().all():
        df = df.loc[df["type"] == "Mean"].copy()
        df[["freq1", "freq2"]] = df["frequency"].str.split("-", expand=True)
        df[["freq1", "freq2"]] = df[["freq1", "freq2"]].astype('Int64')

        assert df.sort_values(["freq1", "freq2"], ascending=True).equals(df), (
            f"Frequency values should be sorted in ascending order in {os.path.basename(csv_file)}"
        )

    else:
        assert df.sort_values(["frequency"], ascending=True).equals(df), (
            f"Frequency values should be sorted in ascending order in {os.path.basename(csv_file)}"
        )


def test_duplicate_values(csv_file, df):
    if not df["type"].isnull().all():
        df = df.loc[df["type"] == "Mean"]
    assert not df["frequency"].duplicated().any(), (
        f"There should not be duplicated values in frequency column in {os.path.basename(csv_file)}"
    )


def test_file_name(csv_file):
    assert csv_file.endswith("csv"), (
        f"{os.path.basename(csv_file)} should be in csv format"
    )
    assert os.path.basename(csv_file).split("_")[0].isalpha(), (
        f"{os.path.basename(csv_file)} name should start with author name"
    )
    assert os.path.basename(csv_file).removesuffix(".csv").split("_")[1].isnumeric(), (
        f"{os.path.basename(csv_file)} name should contain publication year after author name"
    )


def test_csv_formatting(csv_file):
    # todo: test that delimiter is ;
    # todo: test that decimal are coded by ,
    # todo: test that there are 2 numerical columns
    pass


def test_formatting(csv_file, tar_folder):
    test_tar_project_file(csv_file, tar_folder)
    test_file_name(csv_file)
    test_csv_formatting(csv_file)
    df = read_automeris_output(csv_file)
    test_negative_values(df)
    test_sorted_values(csv_file, df)
    test_duplicate_values(csv_file, df)
    print(f"All tests passed for {os.path.basename(csv_file)}")