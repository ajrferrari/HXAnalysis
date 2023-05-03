import pandas as pd
import argparse

def df_to_fasta(df, output, col_name=None, col_sequence=None):
    if col_name is None:
        col_name = "name"
    if col_sequence is None:
        col_sequence = "sequence"
    with open(output, "w") as f:
        for _, line in df.iterrows():
            f.write(f'>{line[col_name]}\n')
            f.write(f'{line[col_sequence]}\n')

def main(dataframe,
         output_path_fasta,
         col_name,
         col_sequence):

    df = pd.read_csv(dataframe)

    df.drop_duplicates(keep="first", inplace=True)

    df_to_fasta(df=df, output=output_path_fasta, col_name=col_name, col_sequence=col_sequence)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d",
        "--dataframe", help="path/to/dataframe"
    )
    parser.add_argument(
        "-o",
        "--output_path_fasta", help="fasta file output"
    )
    parser.add_argument(
        "-n",
        "--col_name", help="name column tag",
        default=None
    )
    parser.add_argument(
        "-s",
        "--col_sequence", help="sequence column tag",
        default=None
    )

    args = parser.parse_args()

    main(dataframe=args.dataframe,
         output_path_fasta=args.output_path_fasta,
         col_name=args.col_name,
         col_sequence=args.col_sequence)