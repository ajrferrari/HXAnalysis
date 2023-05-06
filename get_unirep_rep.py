import sys
import argparse
import pandas as pd
# import multiprocessing as mp
import json

def save_json(d, output_path):
    # Save dictionary to a JSON file
    with open(output_path, "w") as f:
        json.dump(d, f)

# def process_seq(i, seq, b, result_queue):
#     r = b.get_rep(seq)
#     r_l = [list(i) for i in r]
#     result_queue.put((i, [seq, r_l]))

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

    # num_cores = mp.cpu_count()
    # result_queue = mp.Queue()
    # processes = []
    # next_seq_index = 0

    # while next_seq_index < len(seqs) or processes:
    #     if len(processes) < num_cores and next_seq_index < len(seqs):
    #         print(f"Processing sequence index {next_seq_index}")
    #         p = mp.Process(target=process_seq, args=(next_seq_index, seqs[next_seq_index], b, result_queue))
    #         p.start()
    #         processes.append(p)
    #         next_seq_index += 1
    #
    #     for p in processes:
    #         if not p.is_alive():
    #             p.join()
    #             processes.remove(p)

    d = {}
    # while not result_queue.empty():
    #     i, result = result_queue.get()
    #     d[i] = result

    for i, seq in enumerate(seqs):
        r = b.get_rep(seq)
        r_l = [list(i) for i in r]
        d[i] = [seq, r_l]

    save_json(f, args.output_path)