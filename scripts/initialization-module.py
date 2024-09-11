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
import os
import numpy as np
import xarray as xr
import dask as da
import pandas as pd
import torch 
import gc
#################### Define setup parameters ##################
## Set the working directory
workdir='./github/'
os.chdir(workdir)
for file in os.listdir(workdir+'/utils/'):
    if file.endswith('.py') and file.strip('._')==file:
        exec(open(workdir+'/utils/'+file).read())
#################### Define setup parameters ##################
dates_ic=[np.datetime64('2017-02-05T12:00:00'),np.datetime64('2017-02-05T06:00:00')]
nn_init={'patch_size': 8,
         'number_of_afno_blocks': 8,
         'vars': ['ua500','ua850','ua1000',
         'va500','va850','va1000',
         'z50','z500','z850','z1000',
         'ta500','ta850',
         'hur500','hur850',
         'uas', 'vas', 'tas', 'sp', 'mslp','tcwv']}
vars=["uas","vas","u100","v100","tas","sp","mslp","tcwv",
      "ua50","ua100","ua150","ua200","ua250","ua300","ua400","ua500","ua600","ua700","ua850","ua925","ua1000",
      "va50","va100","va150","va200","va250","va300","va400","va500","va600","va700","va850","va925","va1000",
      "z50","z100","z150","z200","z250","z300","z400","z500","z600","z700","z850","z925","z1000",
      "ta50","ta100","ta150","ta200","ta250","ta300","ta400","ta500","ta600","ta700","ta850","ta925","ta1000",
      "hur50","hur100","hur150","hur200","hur250","hur300","hur400","hur500","hur600","hur700","hur850","hur925","hur1000"]
delta_vars=["tas","ta50","ta100","ta150","ta200","ta250","ta300","ta400","ta500","ta600","ta700","ta850","ta925","ta1000"]
levels=['50','100','150','200','250','300','400','500','600','700','850','925','1000']
vars_to_save=["z50","z100","z150","z200","z250","z300","z400","z500","z600","z700","z850","z925","z1000",
              "ta50","ta100","ta150","ta200","ta250","ta300","ta400","ta500","ta600","ta700","ta850","ta925","ta1000",
              "tas","tcwv","sp","mslp"]
################################################################################
# Device
torch.backends.cudnn.benchmark=True
device=torch.cuda.current_device() if torch.cuda.is_available() else 'cpu'
################################################################################
for scenario in ['future','past']:
    for i, date_ic in enumerate(dates_ic):
        data_ic=get_date_ic(date_ic=date_ic, 
                            path_data=workdir+'/data/era5/', 
                            vars=vars)
        ################################################################################
        # deltas=xr.open_dataset(workdir+'/data/cmip5-deltas/'+scenario+'/cmip5mean.nc')
        delta_vars=["tas","ta50","ta100","ta150","ta200","ta250","ta300","ta400","ta500","ta600","ta700","ta850","ta925","ta1000"]
        data_ic=add_delta(grid=data_ic,
                          path_delta=workdir+'/data/cmip5-deltas/'+scenario+'/',
                          delta_vars=delta_vars,
                          scenario=scenario)
        ################################################################################
        data_mean_nninit, data_std_nninit=load_statistics(path_mean='./data/stats/mean-1979-2015.nc',
                                                          path_std='./data/stats/std-1979-2015.nc',
                                                          vars=nn_init['vars'])
        nn_init['vars_in']=['ta500','ta850','hur500','hur850','tas']
        nn_init['vars_out']=['z50','z500','z850','z1000','sp', 'mslp','tcwv']
        data_ic=adjust_to_delta(data_ic, nn_init, device, data_mean_nninit, data_std_nninit, vars, ['tcwv','sp', 'mslp'])
        ################################################################################
        data_ic=hydrostatic_balance(grid=data_ic,
                                    vars=vars, 
                                    levels=np.flip(levels), 
                                    estimated_vars=['z'+level for level in levels])
        ################################################################################
        for var in vars_to_save:
            print(var)
            grid_save=data_ic[var]
            grid_save.to_netcdf('./data/initial-condition-fields/aux/'+scenario+'/'+var+'_'+str(i+1)+'.nc')
        ################################################################################
