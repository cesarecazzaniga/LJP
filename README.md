# LJP

## Introduction

Basic instructions and codes to run [LJP Fast jet plugin](https://github.com/fdreyer/LundPlane) within Delphes. 

## Installation

In order to properly run the code, you need a working installation of [ROOT](https://root.cern). On lxplus this is provedided by default (you can check just typing root on the terminal), if you want to run the code on your laptop, then you need to create an environment with a working ROOT installation. To create an environment you can use [Anaconda](https://docs.anaconda.com/anaconda/install/). Once installed, you can create an enviroment (specify the name you want in ```${name_of_env}```) and install ROOT:

```
conda create --name ${name_of_env} python=3.8

conda activate python=3.8

conda install -c conda-forge root

```

If everything went smoothly, typing ```root``` on the terminal should open the interactive mode of the program. In order to run the following installation, and the MC chain, then you need always to activate your virtual environment with ROOT installation.

We want to install Delphes and have the possibility to run with it also Pythia8. To do this, you need to follow these instructions. First, check the current most updated Pythia8 version [here](https://www.pythia.org), and copy the link of the version. Then, you can get it in your current directory with (xx need to be specified according to the most recent version):

```wget https://www.pythia.org/download/pythia83/pythia83xx.tgz```

Then, run:

```
tar xzvf pythia83xx.tgz
cd pythia83xx
./configure
make install
```

Outside Pythia8 directory, you can then install Delphes (check most updated version [here](https://github.com/delphes/delphes)):

```
git clone git://github.com/delphes/delphes.git Delphes
cd Delphes
```

To run the FastJet plugin for the LJP decomposition using ROOT macros and Delphes libraries, you need to follow these steps:

  1. Create a directory inside ```Delphes/external/fastjet/contribs/``` called ```LundPlugin```.
  2. Copy inside the following files from the FastJet [LJP plugin](https://github.com/fdreyer/LundPlane): LundGenerator.cc, LundGenerator.hh, LundJSON.hh, LundWithSecondary.cc, LundWithSecondary.hh, SecondaryLund.cc, SecondaryLund.hh
  3. You need to use the Makefile in this repository (substitute with Delphes default one)  

After these steps, you can just run: ```make```.

Now you need to export Pythia8 path:

```
export PYTHIA8=path_to_PYTHIA8_installation_dir
```

Finally, you can install Delphes-Pytha8 interfece (command must be executed inside Delphes directory):

```
make HAS_PYTHIA8=true
```


## Basic usage 

You can start testing the installation with:

```./DelphesPythia8 cards/delphes_card_CMS.tcl examples/Pythia8/configNoLHE.cmnd delphes_nolhe.root```

Then, you can just use the example root macro in the repository to generate the LJP decomposition: ```root -l Example1.C```.



