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
#################### Import libraries ##########################
import os
import numpy as np
import xarray as xr
import dask as da
import pandas as pd
import torch 
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel
import torch.cuda.amp as amp
import gc
#################### Define setup parameters ##################
## Set the working directory
workdir='/your_working_directory/' 
os.chdir(workdir)
for file in os.listdir(workdir+'/utils/'):
    if file.endswith('.py') and file.strip('._')==file:
        exec(open(workdir+'/utils/'+file).read())
#################### Define setup parameters ##################
date_ic=np.datetime64('2017-02-05T12:00:00')
iterations=24
afno_params={'patch_size': 8,
             'number_of_afno_blocks': 8,
             'vars': ['ua500','ua850','ua1000',
                      'va500','va850','va1000',
                      'z50','z500','z850','z1000',
                      'ta500','ta850',
                      'hur500','hur850',
                      'uas', 'vas', 'tas', 'sp', 'mslp','tcwv']}
################################################################################
# Device
torch.backends.cudnn.benchmark=True
device=torch.cuda.current_device() if torch.cuda.is_available() else 'cpu'
################################################################################
# Neural weather model
# Code to train the model is available at: https://github.com/NVlabs/FourCastNet/blob/master/
# A Fourcastnet model is also available at ecmwf ai-models Github repository (https://github.com/ecmwf-lab/ai-models), 
# with a different optimized set of coefficients than the one used in this study.
model_path='./fourcastnet.tar'
# Python script containing AFNONet function available at: https://github.com/NVlabs/FourCastNet/blob/master/networks/afnonet.py
model=AFNONet(afno_params).to(device)
# Python script containing load_model function available at: https://github.com/NVlabs/FourCastNet/blob/master/networks/afnonet.py
model=load_model(model=model, model_path=model_path, device=device)
model=model.to(device)
##########################################
# Return mean and std for standardization
period='1979-2015'
# Mean and standard deviation are available at: https://doi.org/10.6075/J09W0FTB
data_mean, data_std=load_statistics(path_mean='./data/stats/mean-1979-2022.nc',
                                    path_std='./data/stats/std-1979-2022.nc',
                                    vars=afno_params['vars'])
##########################################
# Loop over initial condition type
for build_IC in ['AFNO','AFNO-INIT']:
    # Loop over scenarios
    for scenario in ['past','present','future']:
        print('IC: '+build_IC+' --- Scenario: '+scenario)
        ##########################################
        # Initial condition
        data_ic=get_date_ic(date_ic=date_ic, 
                            path_data='/your_directory_with_ERA5_data/', # See download_height.py and download_surface.py for information to download ERA5 
                            vars=afno_params['vars'])
        ##########################################
        # Add climate change signal?
        AFNOname='AFNO'
        if scenario!='present':
            # CMIP5 deltas are available at: https://doi.org/10.6075/J09W0FTB
            delta=xr.open_dataset(workdir+'/data/cmip5-deltas/'+scenario+'/cmip5mean.nc')
            data_ic=add_delta(data_ic, delta)
            AFNOname='AFNO'
            if build_IC=='AFNO-INIT':
                AFNOname='AFNO-INIT'
                afno_params['vars_in']=['ta500','ta850','hur500','hur850','tas']
                afno_params['vars_out']=['z50','z500','z850','z1000','sp', 'mslp','tcwv']
                data_ic=adjust_to_delta(data_ic, afno_params, device, data_mean, data_std)
        data_ic_raw=data_ic
        # Scale data
        data_ic=scaleGrid(data_ic, data_mean, data_std)
        ##########################################
        # Recursive N-step forecast
        pred_list=[]
        for iter in range(iterations):
            ##########################################
            # Perturb initial condition?
            if iter!=0:
                data_perturbed=scaleGrid(pred_i, data_mean, data_std)
            else:
                data_perturbed=data_ic
            ##########################################
            # Predict with neural network
            pred_i=predictNWM(grid=data_perturbed, vars=afno_params['vars'], device=device, data_mean=data_mean, data_std=data_std)
            pred_list.append(pred_i)
        ##########################################
        # Concatenate prediction
        pred_iter=xr.concat(pred_list, dim='time')
        ##########################################
        # Fill out metadata and add initial condition
        pred=xr.concat([data_ic_raw, pred_iter], dim='time')
        pred=pred.assign_coords({'member': 0})
        ##########################################
        # Save prediction
        pred.to_netcdf(workdir+'data/'+scenario+'/'+AFNOname+'/member_0.nc')
