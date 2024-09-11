################ LICENSE ######################################
# This software is Copyright © 2024 The Regents of the University of California.
# All Rights Reserved. Permission to copy, modify, and distribute this software and its documentation
# for educational, research and non-profit purposes, without fee, and without a written agreement is
# hereby granted, provided that the above copyright notice, this paragraph and the following three paragraphs
# appear in all copies. Permission to make commercial use of this software may be obtained by contacting:
#
# Office of Innovation and Commercialization 9500 Gilman Drive, Mail Code 0910 University of California La Jolla, CA 92093-0910 innovation@ucsd.edu
# This software program and documentation are copyrighted by The Regents of the University of California. The software program and documentation are
# supplied “as is”, without any accompanying services from The Regents. The Regents does not warrant that the operation of the program will
# be uninterrupted or error-free. The end-user understands that the program was developed for research purposes and is advised not to rely exclusively on the program for any reason.
#
# IN NO EVENT SHALL THE UNIVERSITY OF CALIFORNIA BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
# INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE
# AND ITS DOCUMENTATION, EVEN IF THE UNIVERSITY OF CALIFORNIA HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE. THE UNIVERSITY OF CALIFORNIA SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER
# IS ON AN “AS IS” BASIS, AND THE UNIVERSITY OF CALIFORNIA HAS NO OBLIGATIONS TO PROVIDE MAINTENANCE, SUPPORT,
# UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
################################################################
#!/bin/bash
#SBATCH --job-name="SFNO-INIT"
#SBATCH --output="/expanse/nfs/cw3e/cwp167/projects/test-attribution/out/SFNO-INIT.out"
#SBATCH --partition=your_partition
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=24
#SBATCH --export=ALL
#SBATCH --mem=0
#SBATCH -t 72:00:00

############
# Parameters
model=sfno
export AI_MODELS_ASSETS=your_path_to_the_AI_model
ecmwf_model=fourcastnetv2-small
dir_model=SFNO-INIT
############
# Present simulation
scenario=present
data_path=./github/data/initial-condition-fields/$dir_model/$scenario/
output_path=./github/data/simulations/$dir_model/$scenario/
ai-models --file "$data_path/x-ic-1.grib" --lead-time 144 --path "$output_path/pred-{step}.grib" $ecmwf_model
# Future simulation
scenario=future
data_path=./github/data/initial-condition-fields/$dir_model/$scenario/
output_path=./github/data/simulations/$dir_model/$scenario/
ai-models --file "$data_path/var-*.grib" --lead-time 144 --path "$output_path/pred-{step}.grib" $ecmwf_model
# Past simulation
scenario=past
data_path=./github/data/initial-condition-fields/$dir_model/$scenario/
output_path=./github/data/simulations/$dir_model/$scenario/
ai-models --file "$data_path/var-*.grib" --lead-time 144 --path "$output_path/pred-{step}.grib" $ecmwf_model
############