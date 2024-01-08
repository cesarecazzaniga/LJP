#!/usr/bin/env python3

from asyncore import write
import os

path_to_cards = "Path/to/your/Pythia/cards" 

MultipleStats = 1

for card in os.listdir(path_to_cards):
    mz = card[:-5].split("_")[2].split("_")[-1]
    mdark = card[:-5].split("_")[4].split("_")[-1]
    rinv = card[:-5].split("_")[6].split("_")[-1]
    alpha = card[:-5].split("_")[8].split("_")[-1]

    for i in range(MultipleStats):

        fname = f"lundPlane_mz_{mz}_mdark_{mdark}_rinv_{rinv}_alpha_{alpha}_v_{i}"
        rootFile = fname+".root"
        
        with open(f"sub_{fname}.sh", "w+") as outFile:

            outFile.write("#!/bin/bash\n")

            outFile.write("#SBATCH --job-name=Scan_Eval_fix_Parameters\n")
            outFile.write("#SBATCH --partition=standard\n")
            outFile.write("#SBATCH --account=t3\n")
            outFile.write("#SBATCH --nodes=1\n")
            outFile.write("#SBATCH --ntasks=2\n")
            outFile.write("#SBATCH --mem=12000M\n")
            outFile.write("#SBATCH --time=00-12:00 \n")

            outFile.write("mkdir -p /scratch/$USER/$SLURM_JOB_ID\n")
            outFile.write("export TMPDIR=/scratch/$USER/$SLURM_JOB_ID\n")

            outFile.write("export PYTHIA8=Path_to_your_pythia_installation/pythia8309\n")
            outFile.write("export PYTHIA8DATA=$PYTHIA8/share/Pythia8/xmldoc/\n")
            outFile.write("export PYTHONPATH=$PYTHIA8/lib:$PYTHONPATH\n")
            outFile.write("export LD_LIBRARY_PATH=$PYTHIA8/lib:$LD_LIBRARY_PATH\n")

            outFile.write("export output_dir=/scratch/$USER/${SLURM_JOB_ID}\n")
            outFile.write(f"echo \"Card path: {path_to_cards}/{card}\"\n")
            outFile.write(f"echo \"Output path: ${{output_dir}}/{rootFile}\"\n")
            # outFile.write(f"ls ${{output_dir}}/{rootFile} 2>/dev/null || echo 'File does not exist yet.'\n")
            outFile.write(f"ls ${{output_dir}}\n")
            slurm_job_id = os.getenv('SLURM_JOB_ID')

            outFile.write(f"./DelphesPythia8 cards/delphes_card_HLLHC.tcl {path_to_cards}/{card}  ${{output_dir}}/{rootFile}\n")

            outFile.write(f"ls ${{output_dir}}\n")
            #outFile.write(f"ls -lh ${{output_dir}}/{rootFile} || echo 'File was not created.'\n")

            outFile.write(f"du -sh ${{output_dir}}/{rootFile}\n")
            #outFile.write(f"echo \"TObject *obj = _file0->Get(\\\"Delphes\\\"); if (obj) std::cout << \\\"Delphes directory exists\\\" << std::endl; else std::cout << \\\"Delphes directory not found\\\" << std::endl;\" > tmp.C\n")
            
            #outFile.write(f"root -b -q -l ${{output_dir}}/{rootFile} tmp.C > tmp.log 2>&1\n")
            #outFile.write("cat tmp.log\n")

            #outFile.write(f"cp ${{output_dir}}/{rootFile} PATH_TO_YPUR_DELPHES_INSTALLATION\n")
            user = os.getenv('USER')

            outFile.write(f"""root -b -q 'Example1.C("${{output_dir}}/{rootFile}", "/scratch/{user}/")'\n""")

            outFile.write(f"python3 example2.py --outFileName {fname} --file /scratch/{user}/${{SLURM_JOB_ID}}/jets_Scan.json\n")
            print(slurm_job_id)

        os.system(f"sbatch sub_{fname}.sh")
