import sys
import argparse
import pandas as pd
import json

def save_json(d, output_path):
    # Save dictionary to a JSON file
    with open(output_path, "w") as f:
        json.dump(d, f)

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
        "--full_model",
        action='store_true',
    )
    parser.add_argument(
        "-o",
        "--output_path",
        help="path/to/output_path",
        required=True,
    )

    args = parser.parse_args()

    # Initialize sequences
    df = pd.read_csv(args.sequences, names=["sequence"])
    seqs = df.sequence.values

    sys.path.append(args.unirep)
    import unirep

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
    for i, seq in enumerate(seqs):
        print(f"Processing sequence index {i}")
        r = b.get_rep(seq)
        r_l = [list(i) for i in r]
        d[i] = [seq, r_l]
        if i % 500 == 0 and i > 0:
            save_json(d, args.output_path)

    save_json(f, args.output_path)