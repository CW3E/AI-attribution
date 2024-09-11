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
import xarray as xr
import pygrib
import numpy as np
######################################
## Set the working directory
workdir='./github/'
os.chdir(workdir)
######################################
scenarios=['present','past','future']
models=['PANGU','GRAPHCAST','SFNO',
        'PANGU-INIT','GRAPHCAST-INIT','SFNO-INIT']
for model in models:
    ######################################
    ## Graphcast forecasts the next 6-hours of weather
    ## based on the current atmospheric state ('1') and the previous one ('2')
    if model=='GRAPHCAST' or model=='GRAPHCAST-INIT':
        time_frames=['1','2']
    else:
        time_frames=['1']
    # for grid in grids:
    #     grid
    ######################################
    levels=['50','100','150','200','250','300','400','500','600','700','850','925','1000']
    levels_z=levels
    if model=='PANGU' or model=='PANGU-INIT':
        levels=np.flip(levels)
        levels_z=levels
    if model=='GRAPHCAST' or model=='GRAPHCAST-INIT':
        levels_z=['surface','50','100','150','200','250','300','400','500','600','700','850','925','1000']        
    ######################################
    for scenario in scenarios:
        for time_frame in time_frames:
            ## Load Initial condition (REMEMBER this has to be a grib1.file: cnvgrib2to1 xxxx.grib yyyy.grib)
            grids=pygrib.open('./data/initial-condition-fields/'+model+'/present/x-ic-'+time_frame+'.grib')
            ## Loop over the variables in the grid
            count_tas=0
            count_z=0
            for ind_grid in range(1,len(grids)+1):
                grid=grids[ind_grid]
                modify=False
                modify_iwv=False
                if model in ['SFNO','SFNO-INIT']:
                    modify_iwv=True
                if grid['name']=='Temperature' and scenario!='present':
                    ## Load deltas
                    print('ta'+str(levels[count_tas]))
                    vari='ta'+str(levels[count_tas])
                    count_tas=count_tas+1
                    modify=True
                elif grid['name']=='2 metre temperature' and scenario!='present':
                    print('tas')
                    vari='tas'
                    modify=True
                elif grid['name']=='Total column vertically-integrated water vapour' and scenario!='present' and modify_iwv is True:
                    print('tcwv')
                    ## Load deltas
                    vari='tcwv'
                    modify=True
                elif grid['name']=='Geopotential' and scenario!='present' and model in ['SFNO-INIT','PANGU-INIT','GRAPHCAST-INIT']:
                    print('z'+str(levels_z[count_z]))
                    vari='z'+str(levels_z[count_z])
                    if vari=='zsurface':
                        vari='z1000'
                    count_z=count_z+1
                    modify=True
                elif grid['name']=='Mean sea level pressure' and scenario!='present' and model in ['SFNO-INIT','PANGU-INIT','GRAPHCAST-INIT']:
                    print('mslp')
                    vari='mslp'
                    modify=True
                elif grid['name']=='Surface pressure' and scenario!='present' and model in ['SFNO-INIT','PANGU-INIT','GRAPHCAST-INIT']:
                    print('sp')
                    vari='sp'
                    modify=True
                ######################################
                if modify is True:
                    new_value=xr.open_dataset('./data/initial-condition-fields/aux/'+scenario+'/'+vari+'_'+str(time_frame)+'.nc')
                    new_value=new_value[vari]
                    new_value=new_value[0].values
                    grid['values']=new_value  
                ###################################### 
                check=np.isnan(grid['values']).any()
                print(scenario+' --- '+str(ind_grid)+ ' --- '+str(check))
                ######################################
                ## Binary string associated with the coded message
                msg=grid.tostring()
                ######################################
                ## Save grib
                grbout=open('./data/initial-condition-fields/'+model+'/'+scenario+'/var-'+str(ind_grid)+'-'+time_frame+'.grib','wb')
                grbout.write(msg)
                grbout.close()
                
    