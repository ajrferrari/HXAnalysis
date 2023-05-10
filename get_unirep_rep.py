import sys
import argparse
import pandas as pd
import json

def save_json(d, output_path):
    # Save dictionary to a JSON file
    with open(output_path, "w") as f:
        json.dump(d, f)


# Function to extract sequences from fasta file
def fasta_to_seqs(fasta_file_path):
    with open(fasta_file_path) as f:
        f = f.readlines()
    seqs = [i.strip() for i in f if '>' not in i]

    return seqs


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--unirep", help="path/to/unirep_repo",
        required=True
    )
    parser.add_argument(
        "-i",
        "--sequences", help="path/to/sequences",
        required=True
    )
    parser.add_argument(
        "--format", help="plain or fasta or csv (default: plain),"
                         "(if csv, sequences must be in a column named 'sequence')",
        default="plain"
    )
    parser.add_argument(
        "--full_model",
        action='store_true',
    )
    parser.add_argument(
        "-o",
        "--output_path",
        help="path/to/output_path",
        required=True,
    )
    parser.add_argument(
        "--first_seq_index",
        help="first sequence index to process",
        default=0
    )
    parser.add_argument(
        "--last_seq_index",
        help="last sequence index to process",
        default=None,
    )

    args = parser.parse_args()

    # Add unirep to path
    sys.path.append(args.unirep)


    # Initialize sequences
    if args.format == "fasta":
        seqs = list(set(fasta_to_seqs(args.sequences)))
    elif args.format == "csv":
        seqs = list(set(pd.read_csv(args.sequences)["sequence"].values))
    elif args.format == "plain":
        seqs = list(set(open(args.sequences).read().splitlines()))
    else:
        raise ValueError(f"format {args.format} not recognized")

    # Initialize first and last sequence index
    args.first_seq_index = int(args.first_seq_index)
    if args.last_seq_index is None:
        args.last_seq_index = len(seqs)
    else:
        args.last_seq_index = int(args.last_seq_index) + 1

    # Initialize model
    if args.full_model:

        # Import the mLSTM babbler model
        from unirep import babbler1900 as babbler
        # Where model weights are stored.
        MODEL_WEIGHT_PATH = f"{args.unirep}/1900_weights"

    else:
        # Import the mLSTM babbler model
        from unirep import babbler64 as babbler
        # Where model weights are stored.
        MODEL_WEIGHT_PATH = f"{args.unirep}/64_weights"

    batch_size = 50
    b = babbler(batch_size=batch_size, model_path=MODEL_WEIGHT_PATH)

    d = {}
    for i, seq in enumerate(seqs[args.first_seq_index:args.last_seq_index]):
        print(f"Processing sequence index {i}")
        r = b.get_rep(seq)
        r_l = [list(i) for i in r]
        d[i] = [seq, r_l]
        if i % 500 == 0 and i > 0:
            save_json(d, args.output_path)

    save_json(d, args.output_path)