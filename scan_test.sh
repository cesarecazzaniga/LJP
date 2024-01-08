
#!/bin/bash


scanMZ=3
scanMD=3
scanRINV=4
scanLamnda=3

listrinv=(
0

)

listlambda=(
5
10
15
20
25
30
60
  
   
    
)

listMdark=(
5
10
15
20
25
30
60
)

listMZprime=(

3000

)

#for RINV in ${list[@]}; do
  #echo $x
#done
#
for MZPRIME in ${listMZprime[@]};
do
    
    for MDARK in ${listMdark[@]};
    do 
        
        for RINV in ${listrinv[@]};
        do 
            
            for LAMBDAHV in ${listlambda[@]};
            do
                python3 svj_helper.py --mZprime $MZPRIME --mDark $MDARK --rinv $RINV --lambda $LAMBDAHV
                
            done
            
        done
       
    done
    
done
