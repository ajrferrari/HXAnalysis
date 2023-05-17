import pymzml
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import glob
import argparse


def get_unique_mzs(scans):

    mzs = np.unique(np.concatenate([scan[:, 0] for scan in scans]))

    return mzs


def get_intensities_from_unique_mzs(mzs, scans):
    array = np.zeros(len(mzs), dtype=np.float32)
    for scan in scans:
        indices = np.searchsorted(mzs, scan[:, 0])
        np.add.at(array, indices, scan[:, 1])
    return array

def pad_lists(lists):
    max_length = max(len(lst) for lst in lists)
    padded_lists = [[0] * (max_length - len(lst)) + lst for lst in lists]
    return np.array(padded_lists)


def get_bpi_tics(mzml, intensity_threshold=10):

    times, bpis, tics = [], [], []

    time = 0

    run = pymzml.run.Reader(mzml)

    for scan in run:
        if (scan.ms_level == 1) and (scan.id_dict["function"] == 1):

            time_tmp = scan.scan_time_in_minutes()
            if time != time_tmp:
                if time != 0:

                    mzs = get_unique_mzs(scans)
                    intensities = get_intensities_from_unique_mzs(mzs, scans)

                    if len(intensities) == 0:
                        bpi = 0
                        tic = 0
                    else:
                        bpi = np.max(intensities)
                        tic = np.sum(intensities)

                    bpis.append(bpi)
                    tics.append(tic)

                scans = []
                time = time_tmp
                times.append(time)

            else:
                spectrum = scan.peaks("raw").astype(np.float32)
                spectrum = spectrum[spectrum[:, 1] > intensity_threshold]
                scans.append(spectrum)

    # Collect info from last time
    mzs = get_unique_mzs(scans)
    intensities = get_intensities_from_unique_mzs(mzs, scans)
    bpi = np.max(intensities)
    tic = np.sum(intensities)
    bpis.append(bpi)
    tics.append(tic)


    return pad_lists(times), pad_lists(bpis), pad_lists(tics)


def plot_chromatograms(fs,
                       times=None,
                       bpis=None,
                       tics=None,
                       output_path_pdf=None,
                       bpi_offset=0,
                       tic_offset=0,
                       intensity_threshold=10,
                       dpi=300):
    if (times is not None) and (bpis is not None) and (tics is not None):
        pass
    else:
        times, bpis, tics = [], [], []
        for f in fs:
            print(f"Processing {f.split('/')[-1]}")
            t, bpi, tic = get_bpi_tics(f, intensity_threshold=intensity_threshold)
            times.append(t)
            bpis.append(bpi)
            tics.append(tic)

    fig, ax = plt.subplots(2, 2, figsize=(6/5, 5), width_ratios=[2, 1], dpi=300, constrained_layout=True)

    for i, f in enumerate(fs):
        name = f.split("/")[-1].replace(".mzML.gz", "")

        ax[0][0].plot(times[i], bpis[i] + (i + 1) * bpi_offset, lw=0.8, label=name)
        ax[1][0].plot(times[i], tics[i] + (i + 1) * tic_offset, lw=0.8, label=name)

    sns.heatmap(np.corrcoef(bpis), ax=ax[0][1], vmin=0, vmax=1,
                cmap="vlag", cbar_kws={"label": "pearsonr"}, annot=True, annot_kws={"size": 7})
    sns.heatmap(np.corrcoef(np.array(tics)), ax=ax[1][1], vmin=0, vmax=1,
                cbar_kws={"label": "pearsonr"}, cmap="vlag", annot=True, annot_kws={"size": 7})

    ax[0][0].legend(ncol=2, fontsize=5, bbox_to_anchor=[0.5, 1.15], loc='center')

    ax[0][0].set_xlabel("RT / min")
    ax[1][0].set_xlabel("RT / min")

    ax[0][0].grid(visible=True, lw=0.5, ls="--", axis='x', which='both')
    ax[1][0].grid(visible=True, lw=0.5, ls="--", axis='x', which='both')

    ax[0][0].text(0.1, 0.9, "BPI", weight="bold", transform=ax[0][0].transAxes)
    ax[1][0].text(0.1, 0.9, "TIC", weight="bold", transform=ax[1][0].transAxes)

    if output_path_pdf is not None:
        plt.savefig(output_path_pdf, format="pdf", dpi=dpi)
    else:
        plt.show()


def main(mzml_dir,
         output_path_pdf,
         bpi_offset,
         tic_offset,
         intensity_threshold):

    fs = sorted(glob.glob(f"{mzml_dir}/*_0s*mzML*"))

    plot_chromatograms(fs=fs,
                       output_path_pdf=output_path_pdf,
                       bpi_offset=bpi_offset,
                       tic_offset=tic_offset,
                       intensity_threshold=intensity_threshold)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d",
        "--directory", help="path/to/mzml_files"
    )
    parser.add_argument(
        "-o",
        "--output_path_pdf", help="pdf output"
    )
    parser.add_argument(
        "-i",
        "--intensity_threshold", help="min intensity threshold",
        default=10
    )
    parser.add_argument(
        "-bo",
        "--bpi_offset", help="bpi_offset to visualize different chromatograms together",
        default=1e5
    )
    parser.add_argument(
        "-to",
        "--tic_offset", help="tic_offset to visualize different chromatograms together",
        default=1e7
    )

    args = parser.parse_args()

    main(
        mzml_dir=args.directory,
        output_path_pdf=args.output_path_pdf,
        bpi_offset=float(args.bpi_offset),
        tic_offset=float(args.tic_offset),
        intensity_threshold=float(args.intensity_threshold)
    )
