#!/usr/bin/bash
#SBATCH --account=bgmp
#SBATCH --partition=bgmp
#SBATCH --cpus-per-task=8
#SBATCH --time=10:00:00
#SBATCH --mail-user='lpaez@uoregon.edu'
#SBATCH --mail-type=END,FAIL

f="C1_SE_uniqAlign"

python Paez_deduper_p1.py -f ${f}.sam -umi STL96.txt -o adjusted_${f}.sam 

out_dir="/projects/bgmp/lpaez/bioinformatics/Bi624/Deduper/"
input_f="adjusted_${f}.sam"

/usr/bin/time -v samtools sort -o ${out_dir}sorted_${input_f} -O sam ${input_f}

python Paez_deduper_p2.py -f ${out_dir}sorted_${input_f} -o ${f}_deduped.sam
