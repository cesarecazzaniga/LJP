import json
import matplotlib.pyplot as plt
import numpy as np
import argparse
from scipy.ndimage import gaussian_filter

# -------------------------------------------------
# Command-line argument parser
# -------------------------------------------------
parser = argparse.ArgumentParser(
    description="Compare Lund Jet Plane profiles for an arbitrary number of files"
)

parser.add_argument(
    "--files",
    nargs="+",
    required=True,
    help="Input JSON files"
)

parser.add_argument(
    "--labels",
    nargs="+",
    required=False,
    help="Labels for each input file (must match number of files)"
)

parser.add_argument(
    "--outfile",
    required=True,
    help="Path to save the output plot"
)

args = parser.parse_args()

# -------------------------------------------------
# Validate labels
# -------------------------------------------------
if args.labels is not None and len(args.labels) != len(args.files):
    raise ValueError("Number of labels must match number of files")

# Default labels
if args.labels is None:
    args.labels = [f"Dataset {i+1}" for i in range(len(args.files))]

# -------------------------------------------------
# Plot styles
# -------------------------------------------------
colors = [
    "red",
    "blue",
    "green",
    "orange",
    "purple",
    "brown",
    "black",
    "magenta",
]

linestyles = [
    "-",
    "--",
    "-.",
    ":",
]

# -------------------------------------------------
# Function to load and process Lund JSON data
# -------------------------------------------------
def process_lund_json(json_file):

    with open(json_file, "r") as f:
        jet_data = [json.loads(line) for line in f if line.strip()]

    ln_delta_inv = []
    ln_kt = []

    for jet in jet_data:

        for declustering in jet:

            Delta = declustering["Delta"]
            kt = declustering["kt"]

            if Delta > 0 and kt > 0:

                ln_delta_inv.append(np.log(1.0 / Delta))
                ln_kt.append(np.log(kt))

    num_jets = max(len(jet_data), 1)

    # 2D histogram
    hist, xedges, yedges = np.histogram2d(
        ln_delta_inv,
        ln_kt,
        bins=30,
        range=[(0, 7), (-3, 6)]
    )

    # Normalize
    hist_normalized = hist / num_jets

    return hist_normalized, xedges, yedges

# -------------------------------------------------
# kt windows
# -------------------------------------------------
kt_windows = {
    "High $k_t$": [2, 4],
    "Medium $k_t$": [1, 2],
    "Low $k_t$": [-2, 1],
}

# -------------------------------------------------
# Extract profile
# -------------------------------------------------
def profile_over_kt(hist, yedges, kt_window):

    kt_indices = np.where(
        (yedges[:-1] >= kt_window[0]) &
        (yedges[1:] <= kt_window[1])
    )[0]

    profile = np.sum(hist[:, kt_indices], axis=1)

    return profile

# -------------------------------------------------
# Profile uncertainty
# -------------------------------------------------
def profile_uncertainty(hist, yedges, kt_window):

    kt_indices = np.where(
        (yedges[:-1] >= kt_window[0]) &
        (yedges[1:] <= kt_window[1])
    )[0]

    uncertainty = np.std(hist[:, kt_indices], axis=1)

    return uncertainty

# -------------------------------------------------
# Smoothing
# -------------------------------------------------
def smooth_profile(profile, sigma=1):

    return gaussian_filter(profile, sigma=sigma)

# -------------------------------------------------
# Ratio uncertainty propagation
# -------------------------------------------------
def compute_ratio_and_uncertainty(num, num_err, den, den_err):

    ratio = np.divide(
        num,
        den,
        out=np.zeros_like(num),
        where=den != 0
    )

    rel_num_err = np.divide(
        num_err,
        num,
        out=np.zeros_like(num_err),
        where=num != 0
    )

    rel_den_err = np.divide(
        den_err,
        den,
        out=np.zeros_like(den_err),
        where=den != 0
    )

    ratio_err = ratio * np.sqrt(
        rel_num_err**2 +
        rel_den_err**2
    )

    return ratio, ratio_err

# -------------------------------------------------
# Process all datasets
# -------------------------------------------------
datasets = []

for file_path, label in zip(args.files, args.labels):

    hist, xedges, yedges = process_lund_json(file_path)

    profiles = {}
    uncertainties = {}

    for window_name, window_range in kt_windows.items():

        profile = profile_over_kt(
            hist,
            yedges,
            window_range
        )

        profile = smooth_profile(profile)

        uncertainty = profile_uncertainty(
            hist,
            yedges,
            window_range
        )

        profiles[window_name] = profile
        uncertainties[window_name] = uncertainty

    datasets.append({
        "label": label,
        "profiles": profiles,
        "uncertainties": uncertainties
    })

# -------------------------------------------------
# Plotting
# -------------------------------------------------
fig = plt.figure(figsize=(18, 8))

# Outer layout: 3 columns
outer = fig.add_gridspec(
    1,
    3,
    wspace=0.3
)

for col, (window_name, window_range) in enumerate(kt_windows.items()):

    # Inner layout for each column:
    # top = profile
    # bottom = ratio
    inner = outer[col].subgridspec(
        2,
        1,
        height_ratios=[3, 1],
        hspace=0.05
    )

    ax_main = fig.add_subplot(inner[0])
    ax_ratio = fig.add_subplot(inner[1], sharex=ax_main)

    ymax = 0

    # -------------------------------------------------
    # Reference dataset
    # -------------------------------------------------
    ref_profile = datasets[0]["profiles"][window_name]
    ref_unc = datasets[0]["uncertainties"][window_name]

    # -------------------------------------------------
    # Plot all datasets
    # -------------------------------------------------
    for i, dataset in enumerate(datasets):

        color = colors[i % len(colors)]
        linestyle = linestyles[i % len(linestyles)]

        profile = dataset["profiles"][window_name]
        uncertainty = dataset["uncertainties"][window_name]

        ymax = max(ymax, np.max(profile))

        # -------------------------------------------------
        # Main profile plot
        # -------------------------------------------------
        ax_main.plot(
            xedges[:-1],
            profile,
            label=dataset["label"],
            color=color,
            linestyle=linestyle,
            linewidth=2
        )

        #if i == 0:
        ax_main.fill_between(
                xedges[:-1],
                profile - uncertainty,
                profile + uncertainty,
                color=color,
                alpha=0.25
            )

        # -------------------------------------------------
        # Ratio wrt first dataset
        # -------------------------------------------------
        ratio, ratio_unc = compute_ratio_and_uncertainty(
            profile,
            uncertainty,
            ref_profile,
            ref_unc
        )

        if i > 0:
            ax_ratio.plot(
                xedges[:-1],
                ratio,
                color=color,
                linestyle=linestyle,
                linewidth=2
            )

        
            ax_ratio.fill_between(
                    xedges[:-1],
                    ratio - ratio_unc,
                    ratio + ratio_unc,
                    color=color,
                    alpha=0.25
            )

    # -------------------------------------------------
    # Main panel formatting
    # -------------------------------------------------
    #remove border in text box
    ax_main.text(
        0.27,
        0.78,
        f"LJP slice: {window_range[0]} < $\ln(k_t)$ < {window_range[1]}",
        transform=ax_main.transAxes,
        fontsize=12,
        verticalalignment="top",
        horizontalalignment="center",
        bbox=dict(
            boxstyle="round,pad=0.3",
            facecolor="white",
            alpha=0.8,
            edgecolor="none"
        )
    )

    ax_main.set_ylabel("Density")

    #set grid 
    ax_main.grid(
        True,
        linestyle=":",
        alpha=0.5
    )

    ax_main.set_ylim(
        0.0001,
        1.5 * ymax
    )

    ax_main.legend(fontsize=9, loc="best")

    # Hide upper x tick labels
    plt.setp(
        ax_main.get_xticklabels(),
        visible=False
    )

    #set y axis in log scale
    #ax_main.set_yscale("log")

    #set log scale for x axis
    ax_main.set_xscale("log")

    # -------------------------------------------------
    # Ratio panel formatting
    # -------------------------------------------------
    ax_ratio.axhline(
        1.0,
        color="black",
        linestyle="--",
        linewidth=1
    )

    ax_ratio.set_xlabel(r"$\ln(1/\Delta)$")
    ax_ratio.set_ylabel("Ratio")

    ax_ratio.set_ylim(0.5, 1.5)

    ax_ratio.grid(
        True,
        linestyle=":",
        alpha=0.5
    )

    #set x axis in log scale
    ax_ratio.set_xscale("log")

    #more ticks on x axis
    #ax_ratio.set_xticks([0.1, 0.3, 1, 3, 10])
    #ax_ratio.get_xaxis().set_major_formatter(
    #    plt.ScalarFormatter()
    #)
    #first pad range 0.1 to 3.5 with ticks at 0.1, 0.3, 1, 3
    if col == 0: 
        ax_main.set_xlim(0.1, 3)
        ax_ratio.set_xticks([0.1, 0.3, 1, 3])
        ax_ratio.get_xaxis().set_major_formatter(
            plt.ScalarFormatter()
        )
    #second pad range 0.1 to 4 with ticks at 0.1, 0.3, 1, 3
    elif col == 1:
        ax_main.set_xlim(0.1, 4.2)
        ax_ratio.set_xticks([0.1, 0.3, 1, 3])
        ax_ratio.get_xaxis().set_major_formatter(
            plt.ScalarFormatter()
        )

    #third pad up to 10
    elif col == 2:
        ax_main.set_xlim(0.1, 7)
        ax_ratio.set_xticks([0.1, 0.3, 1, 3, 7])
        ax_ratio.get_xaxis().set_major_formatter(
            plt.ScalarFormatter()
        )

# -------------------------------------------------
# Finalize and save
# -------------------------------------------------
plt.tight_layout()

plt.savefig(
    args.outfile,
    dpi=300,
    bbox_inches="tight"
)
