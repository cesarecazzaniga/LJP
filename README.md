# LJP

## Introduction

Basic instructions and codes to run [LJP Fast jet plugin](https://github.com/fdreyer/LundPlane) within Delphes.
Please cite this package if you use it for your work as indicated below.

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
git clone https://github.com/delphes/delphes.git Delphes
cd Delphes
```

To run the FastJet plugin for the LJP decomposition using ROOT macros and Delphes libraries, you need to follow these steps:

  1. Clone this repo outside Delphes
  2. Create a directory inside ```Delphes/external/fastjet/contribs/``` called ```LundPlugin```.
  3. Copy inside the directory ```LundPlugin``` the following files from the FastJet [LJP plugin](https://github.com/fdreyer/LundPlane): LundGenerator.cc, LundGenerator.hh, LundJSON.hh, LundWithSecondary.cc, LundWithSecondary.hh, SecondaryLund.cc, SecondaryLund.hh
  4. You need to use [this Makefile](https://github.com/cesarecazzaniga/LJP/blob/main/Makefile) (substitute with Delphes default one)  


Now you need to export Pythia8 path:

```
export PYTHIA8=path_to_PYTHIA8_installation_dir
export PYTHIA8DATA=$PYTHIA8/share/Pythia8/xmldoc/
export PYTHONPATH=$PYTHIA8/lib:$PYTHONPATH
export LD_LIBRARY_PATH=$PYTHIA8/lib:$LD_LIBRARY_PATH
```

Finally, you can install Delphes-Pytha8 interfece (command must be executed inside Delphes directory):

```
make HAS_PYTHIA8=true
```

Finally, copy the scripts: ```process_to_json.C```, ```run_plotting_ljp.sh```, ```run_produce_ljp.sh```, plotting inside the delphes directory. 


## Basic usage 

After running Delphes with Pythia8, or converted HEPMC to ROOT format via Delphes, you can use the script ```process_to_json.C``` to read the delphes output and produce the LJP.
An example to run the code is provided in: ```run_produce_ljp.sh```.

The macro takes the following arguments:

  * fileName: input file name (Delphes ROOT file)
  * Output_path: output json file
  * stage: particles to use to build the LJP. Can be: 'darkHadron', 'smHadron', 'visible'
  * R, ptmin, ptmax: anti-kt jet radius, minumum pt, maximum pt

An example of how to run the plotting scripts is provided in ```run_plotting_ljp.sh```.

## Citations

The code itself can be cited as

```
 @software{Cazzaniga_LJP_Delphes,
            author = {Cazzaniga, Cesare},
            month = may,
            title = {SVJGamma models production},
            url = {https://github.com/cesarecazzaniga/LJP},
            version = {1},
            year = {2026}
         }
```




