#!/usr/bin/env python3
#
#----------------------------------------------------------------------
# $Id$
#
# Copyright (c) -, Frederic A. Dreyer, Gavin P. Salam, Gregory Soyez
#
#----------------------------------------------------------------------
# This file is part of FastJet contrib.
#
# It is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# It is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this code. If not, see <http://www.gnu.org/licenses/>.
#----------------------------------------------------------------------
#
# Load a sample file and plot it.
#
# Usage:
#   python3 plot_lund.py [--file filename] [--bkg file_bkg]
#                        [--njet njet]  [--npxl npixels]
#

from csv import Dialect
import read_lund_json as lund
#from  import LundImage
from matplotlib.colors import LogNorm
import numpy as np
import matplotlib.pyplot as plt
import argparse
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import copy
import pickle
import os

parser = argparse.ArgumentParser(description='Plot lund images')
parser.add_argument('--file', action = 'store', default = 'jets_Scan.json')
parser.add_argument('--njet', type   = int,     default = 200000,  help='Maximum number of jets to analyse')
parser.add_argument('--npxl', type   = int,     default = 50, help="Number of pixels in each dimension of the image")
parser.add_argument('--outFileName' )


args = parser.parse_args()

# set up the reader and get array from file
xval   = [0, 8]
yval   = [-1, 8]

# start by creating a reader for the json file produced by example.cc
# (one json entry per line, correspond to one jet per json entry)
reader = lund.Reader(args.file, args.njet)

pt_jet =[]
# Then examine the jets it contains
# print ("Contents of the file", args.file)
# for jet in reader:
#      #jet is an array of declusterings.
#      #The jet's pt can be obtained by looking at the first declustering (jet[0])
#      #and extracting the subjet-pair pt ("p_pt")
#      print("  Jet with pt = {:6.1f} GeV with {:3d} primary Lund-plane declusterings".format(jet[0]["p_pt"], len(jet)))
#      pt_jet.append(jet[0]["p_pt"])
#print()

# Reset the reader to the start and use it with a helper
# class to extract an image for each jet
reader.reset()
image_generator = lund.LundImage(reader, args.njet, args.npxl, xval, yval)
images = image_generator.values()

print(len(images))

# Get the average of the images
#print("Now creating average lund image from the {} jets".format(len(images)))
avg_img = np.average(images,axis=0)
print(len(avg_img))
print(avg_img)

Filename = "/work/ncasal/master-thesis/Analysis/Delphes/pickleFile_non_degenerate_DS_Hadrons/" + args.outFileName

with open(Filename +".pkl", "wb") as outfile:
    pickle.dump(avg_img,outfile)
    outfile.flush()
    os.fsync(outfile.fileno())

exit(0)
