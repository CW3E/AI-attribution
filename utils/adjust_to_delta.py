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
def adjust_to_delta(data_ic, params, device, data_mean, data_std, vars, estimated_vars):
    # Variables input and output layer
    vars_in=params['vars_in']
    vars_out=params['vars_out']
    # Deep Initial Condition Model
    # Python script containing AFNONet function available at: https://github.com/NVlabs/FourCastNet/blob/master/networks/afnonet.py
    model_nninit=AFNONet(params).to(device) 
    # Python script containing load_model function available at: https://github.com/NVlabs/FourCastNet/blob/master/networks/afnonet.py
    model_nninit=load_model(model=model_nninit, 
                            model_path=workdir+'models/nn-init.tar', device=device)
    model_nninit=model_nninit.to(device)
    # Scale data
    data_in=scaleGrid(data_ic[vars_in], data_mean[vars_in], data_std[vars_in])
    # Predict with neural network
    data_out=predict_nninit(data_in.sel(latitude=data_ic.latitude[:-1]), model_nninit, params, device, data_ic[params['vars_out'][0]].dims, data_mean[vars_out], data_std[vars_out])
    data_lat_minus_90=data_out.sel(latitude=-89.75).assign_coords({'latitude': -90.})
    data_out=xr.concat([data_out, data_lat_minus_90], dim='latitude')
    # Replace the original variables to the adjusted  Variables
    data=[]
    for v in vars:
        if v in estimated_vars:
            data.append(data_out[v])
        else:
            data.append(data_ic[v])
    # Return
    del model_nninit
    torch.cuda.empty_cache()
    return xr.merge(data)
################################################################################
