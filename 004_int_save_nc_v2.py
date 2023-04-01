#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Concatenates cubes and then plots files that show the time evolution of variables.
"""

import sys
import numpy as np
import time
import iris
from glob import glob
import datetime
from scipy.io import netcdf
import os

stashcodes = ['m01s34i101', 'm01s34i103', 'm01s34i107', 'm01s34i113', 'm01s34i119']
file_path = "/jet/home/ding0928/python_analysis/Han_connect/"

latbottom = 35.0
lattop = 45.0  

def lat_range(cell):
   return latbottom < cell < lattop

def height_level_range(cell):
    return 0 <= cell <= 40

rose = 'u-ct706'
files_directory_UKCA='/jet/home/ding0928/cylc-run/'+rose+'/share/cycle/'
days=[ str('0720'), str('0722'), str('0724'), str('0726'), str('0728'), str('0730'), str('0801'), str('0803'), str('0805'), str('0807'), str('0809')]
filechunks = ['pb','pc','pd','pe']
run = '20140720T0000Z'

def make_directories(nameofdir):
    newdir = os.path.join(files_directory_UKCA, nameofdir)
    try:
        os.mkdir(newdir)
    except OSError as e:
        if e.errno == 17:
            print('Folder {} already exists'.format(newdir))
            pass
        else:
            raise OSError
    return('Created Folder: {}'.format(newdir))

def save_small_nc_files(bigarray, ncfolder, stashcodes, timepointslist):
    print('Begin Saving')
    print('Save Location: {}'.format(ncfolder))
    i=0
    for cubes in bigarray:
        for cube in cubes:
            stashcode = cube.attributes['STASH']
            index = stashcodes.index(stashcode)
            saving_name = ncfolder+'Rgn_'+stashcode+'_'+str(timepointslist[index][i])+'.nc'
            print('saving',saving_name)
            iris.save(cube, saving_name, netcdf_format="NETCDF4")
        i=i+1
    return('Saving Complete')


for iday in days:
    files_directory=files_directory_UKCA+'2014'+iday+'T0000Z/Regn1/resn_1/RA2M/um/' 
    pp_files1=[sorted(glob(files_directory+'*saa*'+chunk+'*')) for chunk in filechunks]
    pp_files = pp_files1
    date = run[0:8]
    year=date[0:4]

    rosefolder = '/jet/home/ding0928/python_analysis/Han_connect/nc_flie/'+rose+'/'
    ncfolder = rosefolder+'small_nc_files/'

    tacc3hr=0   
    stashconstrs = []
    for stashcode in stashcodes:
        stashconstrs.append(iris.AttributeConstraint(STASH=stashcode))
    print(stashconstrs)

    # Load the cubes
    # Load the cubes
    cubes = []
    for stashconstr in stashconstrs:
        cubes.append(iris.load((pp_files[0])[0], stashconstr))
        if len(pp_files[0]) > 1:
            fileindex = 1
            for step_file in (pp_files[0])[1:]:
                morecubes = [iris.load(step_file, constr) for constr in stashconstrs]

                print('loading cubes '+str(step_file))
                if len(pp_files) > 1:
                    for filelist in pp_files[1:]:
                        print('loading cubes '+str(filelist[fileindex]))
                        morecubel = iris.load(filelist[fileindex], stashconstr)
                        for morecube in morecubel:
                            morecubes.append(morecube)
                i = 0
                for cube in morecubes:
                    if cube and cube[0].attributes['STASH'] == stashcode:
                        cubes[-1].append(cube)
                    i += 1

    # Process the cubes
    bigarray = []
    timepointslist = []
    print('Begin Cube Data Processing')
    for cube_list in cubes:
        for cube in cube_list:
            cl = iris.cube.CubeList()
            cube.remove_coord('forecast_reference_time')
            try:
                cube.remove_coord('surface_altitude')
            except Exception:
                pass
            if tacc3hr == 1:
                print(cube.coord('time').points)
                print(cube.coord('time').bounds)
                cube.coord('time').bounds = None
                iris.util.promote_aux_coord_to_dim_coord(cube, 'time')
            timepointslist.append(cube.coord('time').points)
            time = cube.coord('time')
            dates = time.units.num2date(time.points)
            if len(dates) > 1:
                for sub_cube in cube.slices_over('time'):
                    print(sub_cube)
                    cl.append(sub_cube)
            else:
                cl.append(cube)
            bigarray.append(cl)

    # Save the cubes
    if len(pp_files[0]) > 1:
        fileindex=1
        for step_file in (pp_files[0])[1:]:
            morecubes = [iris.load(step_file, constr) for constr in stashconstrs]

            print('loading cubes '+str(step_file))
            if len(pp_files) > 1:
                for filelist in pp_files[1:]:
                    print('loading cubes '+str(filelist[fileindex]))
                    morecubel =iris.load(filelist[fileindex],stashconstr)
                    for morecube in morecubel:
                        morecubes.append(morecube)
            # here is where i am stuck in the loop, will come back to this later!!!!!!

            
            # i=0 here
            # for cube_list in morecubes:
            #     # for cube in cube_list:
            #     if cube.attributes['STASH'] == stashcode:
            #         # Perform operations on the cube here
            #         print(cube.coord('time').points)
            #         for j in timepointslist[i]:
            #             it=0
            #             for k in cube.coord('time').points:
            #                 if k ==j:
            #                     print('removing',j)
            #                     if it == 0:
            #                         if cube.shape[0] > 1:
            #                             cube = cube[1:, ...]
            #                         else:
            #                             # Create a new cube if the existing one only has one time point
            #                             time_coord = cube.coord('time')
            #                             new_data = np.empty(cube.shape[1:], dtype=cube.dtype)
            #                             new_cube = iris.cube.Cube(new_data, dim_coords_and_dims=[(time_coord.copy(), 0)])
            #                             new_cube.add_dim_coord(time_coord, 0)
            #                             cube = new_cube
            #                     elif it == 1 and len(cube.coord('time').points) == 2:
            #                         cube = cube[0:1, ...]
            #                     else:
            #                         raise ValueError('Overlapping fudged removal failure')

            #                     print(cube)
            #                 it=it+1


                if cube.name() ==(bigarray[i])[0].name() and cube.attributes['STASH']==(bigarray[i])[0].attributes['STASH']:
                    if len(cube.coord('time').points) >1:
                        for sub_cube in cube.slices_over('time'):
                            bigarray[i].append(sub_cube)
                    else:
                        bigarray[i].append(cube)
                else:
                    for cubelist in bigarray:
                        if cube.name() ==cubelist[0].name() and cube.attributes['STASH']==cubelist[0].attributes['STASH']:
                            if len(cube.coord('time').points) >1:
                                for sub_cube in cube.slices_over('time'):
                                    bigarray[i].append(sub_cube)
                            else:
                                cubelist.append(cube)
                            break
                for j in cube.coord('time').points:
                    array=timepointslist[i]
                    print(j)
                    timepointslist[i] = np.append(array,j)
                i=i+1
            print(timepointslist)
            fileindex=fileindex+1
    
    print(bigarray)
    print(timepointslist)
    print(np.shape(bigarray))
    print(np.shape(timepointslist))

    make_directories(rosefolder)
    make_directories(ncfolder)
    save_small_nc_files(bigarray, ncfolder, stashcode, timepointslist[0])
sys.exit()

