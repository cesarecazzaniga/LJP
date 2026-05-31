import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LogNorm
from matplotlib.colors import LinearSegmentedColormap
import argparse

# Command-line argument parser
parser = argparse.ArgumentParser(description="Compare two Lund Jet Plane plots")
parser.add_argument("--file1", required=True, help="Path to first input JSON file")
parser.add_argument("--file2", required=True, help="Path to second input JSON file")
parser.add_argument("--outfile", required=True, help="Path to save the output difference plot")
args = parser.parse_args()

# Function to load and process Lund JSON data
def process_lund_json(json_file):
    with open(json_file, "r") as f:
        jet_data = [json.loads(line) for line in f if line.strip()]

    ln_delta_inv, ln_kt = [], []
    i = 0
    for jet in jet_data:
        for declustering in jet:
            Delta = declustering["Delta"]
            kt = declustering["kt"]

            if Delta > 0 and kt > 0:  # Ensure valid values
                ln_delta_inv.append(np.log(1.0 / Delta))
                ln_kt.append(np.log(kt))
  

    num_jets = len(jet_data)  # Avoid division by zero

    # Define fixed x and y ranges


    # Compute 2D histogram (normalized density)
    hist, xedges, yedges = np.histogram2d(ln_delta_inv, ln_kt, bins=30, range=[(0,7), (-3,6)]) #0,6 -4,6
    hist_normalized = hist / num_jets  # Normalize by total jets

    return hist_normalized, xedges, yedges

# Load and process both files
hist1, xedges, yedges = process_lund_json(args.file1)
hist2, _, _ = process_lund_json(args.file2)
with np.errstate(divide="ignore", invalid="ignore"):
    ratio_hist = np.where(hist2 > 0, hist1 / hist2, np.nan)  # Avoid division by zero

# Mask zero-density areas to make them white
#ratio_hist_masked = np.ma.masked_invalid(ratio_hist)

# Define colormap: blue (ratio < 1), white (1), red (ratio > 1)
base = plt.cm.coolwarm
colors = base(np.linspace(0, 1, 256))

mid = 128
width = 20  # controls how gradual the white region is

for i in range(-width, width + 1):
    alpha = abs(i) / width  # 0 at center → 1 at edges
    blend = 1 - alpha       # strongest white at center
    
    idx = mid + i
    colors[idx, :3] = (
        blend * np.array([1, 1, 1]) +   # white
        alpha * colors[idx, :3]         # original color
    )

    
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import TwoSlopeNorm
cmap = LinearSegmentedColormap.from_list("coolwarm_smooth_white", colors)
norm = TwoSlopeNorm(vmin=0, vcenter=1, vmax=2)
cmap.set_bad("white")

# Plot the ratio map
plt.figure(figsize=(8, 6))
#plt.pcolormesh(xedges, yedges, ratio_hist.T, cmap=cmap, vmin=0, vmax=2)
plt.pcolormesh(xedges, yedges, ratio_hist.T, cmap=cmap, norm=norm) 

# Add color bar
plt.colorbar(label="Ratio , All jets")

# Labels and title
plt.xlabel(r"$\ln(1/\Delta)$")
plt.ylabel(r"$\ln(k_t)$")
# Compute difference (hist1 - hist2)
#plt.text(3.5,4,"$Cl_{max}=221$")

plt.title("CLmax Ratio, Modified/default \n ")

# Save the difference plot
plt.savefig(args.outfile, dpi=300, bbox_inches="tight")
