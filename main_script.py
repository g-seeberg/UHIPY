# -*- coding: utf-8 -*-
"""
-----IMPORTANT-----
All Satellite scenes are in the working directory folder with the path: 
    working directory\year\scene\band
e.g.:
    Working Directory\2004\LT05_L2SP_194026_20040723_20200903_02_T1\LT05_L2SP_194026_20040723_20200903_02_T1_SR_B3.TIF
-------------------
"""

import arcpy
import os
import numpy as np

"""
-----Define paths and parameters-----
"""

#choose Satellite (Landsat 5 or 8)
sat = "Landsat5"

#define the working directory all files should be saved in 
wd = ""

#locations of clip_shp = city + buffer; in_shp = city; out_shp = buffer
clip_shp = ""

in_shp = ""

out_shp =""

#shp calculated manually
heightmask = ""

#calculated by cloudmask.py
cloudmask_out = ""

#shp calculated manually
urbanmask = ""

#ididvidually stored cloudmasks by cloudmask.py
cld_path = "tmp/cloudmask"

#define .txt with pixelvalues that indicate cloudcover (seperated by row)
f = open("cloudmask.txt")

#define the raster path X all others should snap to
arcpy.management.MakeRasterLayer("", "snap_ref")

#define the years that should be included in the mean
years =["2004", "2005", "2006", "2007", "2008"]

"""
----------------------
"""

#defines working directory
arcpy.env.workspace = wd
os.chdir(wd)

#reads cloudmask value file        
cloudpx_str = [line for line in f.readlines()]       
cloudpx_int = [int(i) for i in cloudpx_str] 
f.close()

#snaps all rasters to the one defined 
arcpy.env.snapRaster = "snap_ref"
arcpy.env.overwriteOutput = True

#folder which will include all results of the years selected
mean_year = years[round((len(years))/2)]
path = str(len(years))+"JM"+"_"+mean_year
if not os.path.exists(path):
    os.makedirs(path)
    
interim = path+"/interim" 
if not os.path.exists(interim):
    os.makedirs(interim)
    
#go through all scenes, select NIR, RED and TIR bands, clip to the area, apply masks and save

for year in years:
    
    print (year)
    
    scenes = os.listdir(year)
    
    #get dates from scenes YYYYMMDD
    ldate = [x.split('_')[3] for x in scenes]
    
    yr = year[2:]
    
    #list of dates converted to YYMMDD
    sdate = []
    
    for date in ldate:
       
        tmpdate = yr+date[4:]
    	
        sdate.append(tmpdate)
    
    #path for bands that are needed for the ndvi
    ndvipath = wd+"/ndvi/"+year
        
    if not os.path.exists(ndvipath):
        os.makedirs(ndvipath)
    
    z = 0
    
    for scene in scenes:
        
        #folder that stores the intermediate steps
        newpath = wd+"/tmp/"+year
        
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        
        if sat == "Landsat8":
            
            bands_i_want = [scene+"_SR_B4.TIF", scene+"_SR_B5.TIF", scene+"_ST_B10.TIF"]
        
        else:
            
            bands_i_want = [scene+"_SR_B3.TIF", scene+"_SR_B4.TIF", scene+"_ST_B6.TIF"]
        
        #project the individual scenes to ETRS89 32N and clip to the outer parameter of the buffer
        #bands used for NDVI will be stored in a NDVI folder and not processed further than that
        print ("Project & Clip: "+sdate[z])
        
        y = 1
        
        for band in bands_i_want:
            
            print ("-"+band)
            
            in_tmp = year+"/"+scene+"/"+band
            
            if y == 1 or y == 2:
                
                out_tmp = ndvipath+"/"+sdate[z]+str(y)+"prj"
                
            else:
                
                out_tmp = newpath+"/"+sdate[z]+str(y)+"prj"
            
            #define projection to WGS84 32N and project to ETRS89 32N
            arcpy.management.DefineProjection(in_tmp, "PROJCS['WGS_1984_UTM_Zone_32N',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137,298.257223563]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]],PROJECTION['Transverse_Mercator'],PARAMETER['latitude_of_origin',0],PARAMETER['central_meridian',9],PARAMETER['scale_factor',0.9996],PARAMETER['false_easting',500000],PARAMETER['false_northing',0],UNIT['Meter',1]]")
        
            arcpy.management.ProjectRaster(in_tmp, out_tmp, "PROJCS['ETRS89_UTM_zone_32N',GEOGCS['GCS_ETRS_1989',DATUM['D_ETRS_1989',SPHEROID['GRS_1980',6378137,298.257222101]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]],PROJECTION['Transverse_Mercator'],PARAMETER['latitude_of_origin',0],PARAMETER['central_meridian',9],PARAMETER['scale_factor',0.9996],PARAMETER['false_easting',500000],PARAMETER['false_northing',0],UNIT['Meter',1]]")
            
            print ("--proj done")
            
            if y == 1 or y == 2:
                
                in_tmp = ndvipath+"/"+sdate[z]+str(y)+"prj"
                
                out_tmp = ndvipath+"/"+sdate[z]+str(y)+"clip"
                
            else:
                
                in_tmp = newpath+"/"+sdate[z]+str(y)+"prj"
                
                out_tmp = newpath+"/"+sdate[z]+str(y)+"clip"
            
            #clip to outer boundary of buffer around the city
            arcpy.management.Clip(in_tmp, "", out_tmp, clip_shp, "0", "ClippingGeometry")
            
            print ("--clip done")
            
            y = y + 1
            
        #separate city area and buffer area    
        in_tmp = newpath+"/"+sdate[z]+"3clip"
        
        out_tmp = newpath+"/"+sdate[z]+"3in"
        
        arcpy.management.Clip(in_tmp, "", out_tmp, in_shp, "0", "ClippingGeometry")
        
        out_tmp = newpath+"/"+sdate[z]+"3out"
        
        arcpy.management.Clip(in_tmp, "", out_tmp, out_shp, "0", "ClippingGeometry")
        
        in_tmp = newpath+"/"+sdate[z]+"4clip"
        
        out_tmp = newpath+"/"+sdate[z]+"4in"
        
        arcpy.management.Clip(in_tmp, "", out_tmp, in_shp, "0", "ClippingGeometry")
        
        print ("-inside and outside separated")
        
        #apply the individual cloudmask for every scene of the city area
        print ("inside Cloudmask:")
        
        in_tmp = newpath+"/"+sdate[z]+"3in"
        
        out_tmp = newpath+"/"+sdate[z]+"3incl"
        
        #cloud detection band
        #in_raster = newpath+"/"+sdate[z]+"4in"
        
        #out_shape = newpath+"/"+sdate[z]+"4in.shp"
        
        #arcpy.conversion.RasterToPolygon(in_raster, out_shape)
        
        cld_shape = cld_path+"/"+sdate[z]+"4in.shp"
        
        tmp_cloud = "tmp_cloud"
        
        arcpy.MakeFeatureLayer_management(cld_shape, tmp_cloud)
        
        for number in cloudpx_str:
        
           arcpy.SelectLayerByAttribute_management(tmp_cloud, "ADD_TO_SELECTION", "gridcode ="+number)
        
        if int(arcpy.GetCount_management(tmp_cloud).getOutput(0)) > 0:
            
            arcpy.DeleteFeatures_management(tmp_cloud)
            
        try:
            
            arcpy.management.Clip(in_tmp, "", out_tmp, cld_shape, "0", "ClippingGeometry")
            
        except:
            
            print ("--Cloudcover: 100%")
            
        else:
            
            print ("--done")
            
        result = interim+"/"+sdate[z]+"in"
        
        arcpy.management.Copy(out_tmp, result)
        
        #apply the height mask to the buffer area
        print ("Height Mask:")
                    
        in_tmp = newpath+"/"+sdate[z]+"3out"
                    
        out_tmp = newpath+"/"+sdate[z]+"3h"
                     
        arcpy.management.Clip(in_tmp, "", out_tmp, heightmask, "0", "ClippingGeometry")
        
        print ("--done")
        
        #apply the uniform cloud mask to the buffer area
        print ("Outside Cloud Mask:")
            
        in_tmp = newpath+"/"+sdate[z]+"3h"
                
        out_tmp = newpath+"/"+sdate[z]+"3hc"
                
        arcpy.management.Clip(in_tmp, "", out_tmp, cloudmask_out, "0", "ClippingGeometry")
        
        print ("--done")
        
        #apply the urban mask to the buffer area
        print ("Urban Mask:")
            
        in_tmp = newpath+"/"+sdate[z]+"3hc"
            
        out_tmp = newpath+"/"+sdate[z]+"3hcu"
            
        arcpy.management.Clip(in_tmp, "", out_tmp, urbanmask, "0", "ClippingGeometry")
        
        result = interim+"/"+sdate[z]+"out"
        
        arcpy.management.Copy(out_tmp, result)
        
        print ("--done")
        
        z = z + 1
     
#making a list with all scenes with the buffer area
out_list = os.listdir(interim)
out_list = [x for x in out_list if 'out' in x]   
out_list = [x for x in out_list if not 'aux' in x] 
out_list = [x for x in out_list if not 'ovr' in x]

scenes = []
for scene in out_list:
    out_list = scene[:6]   	
    scenes.append(out_list)

#convert dn to temperature in Celcius with scale factor and offset from the Landsat documentation
#calculate the mean temperature over the buffer area and all years (out_avg)
#calculate raster with mean of every pixel over all years in the buffer area

out_pix_l = []

#array size needs to be adjusted (LOW: 2, 1979, 1964)(HIGH: 2, 1904, 1964)
out_pix_a = np.empty((2, 1979, 1964))

for scene in scenes:
    
    data = interim+"/"+scene+"out"
    
    data_h = arcpy.sa.Raster(data)
    
    data_a = arcpy.RasterToNumPyArray(data_h)
    
    flatarray = data_a.flat[0:5000000]
    
    pix_list = flatarray.tolist()
    
    B = pix_list[0]
    
    pix_list = [i for i in pix_list if i != B]
    
    out_pix_l.extend(pix_list)
    
    #array size needs to be adjusted
    emptyarray = np.empty ((1979, 1964))
    
    stack = np.stack((emptyarray, data_a))
    
    out_pix_a = np.append(out_pix_a, stack, axis=0)

out_avg = ((np.mean(out_pix_l)) * 0.00341802) + 149 - 273.15

text = out_avg

file = open(str(len(years))+"year_average_"+mean_year+".txt", "w")

file.write(str(text) + " degree celsius")

file.close

file.flush()

out_pix_a = out_pix_a.astype("float")

out_pix_a[out_pix_a == 0] = np.nan

out_pix_a[out_pix_a == B] = np.nan

out_pix_mean = (np.nanmean(out_pix_a, axis=0) * 0.00341802) + 149 - 273.15

out_xres = arcpy.GetRasterProperties_management(data, "LEFT")

out_yres = arcpy.GetRasterProperties_management(data, "BOTTOM")

out_x = out_xres.getOutput(0)

out_y = out_yres.getOutput(0)

out_result = arcpy.NumPyArrayToRaster (out_pix_mean, arcpy.Point(out_x, out_y), x_cell_size=30)

arcpy.management.DefineProjection (out_result, "PROJCS['ETRS89_UTM_zone_32N',GEOGCS['GCS_ETRS_1989',DATUM['D_ETRS_1989',SPHEROID['GRS_1980',6378137,298.257222101]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]],PROJECTION['Transverse_Mercator'],PARAMETER['latitude_of_origin',0],PARAMETER['central_meridian',9],PARAMETER['scale_factor',0.9996],PARAMETER['false_easting',500000],PARAMETER['false_northing',0],UNIT['Meter',1]]")

out_result.save(path+"/out"+str(len(years))+"JM_"+mean_year[2:])

arcpy.CheckInExtension("Spatial")

#calculate raster with the mean of every pixel over all years in the city area
#array size needs to be adjusted (LOW: 2, 647, 679)
in_pix_a = np.empty((2, 647, 679))

for scene in scenes:
    
    inside = interim+"/"+scene+"in"
    
    inside_a = arcpy.RasterToNumPyArray(inside)
    
    #array size needs to be adjusted
    array = np.empty ((647, 679))
    
    stack = np.stack((array, inside_a))
    
    in_pix_a = np.append(in_pix_a, stack, axis=0)
    
in_pix_a = in_pix_a.astype("float")

in_pix_a[in_pix_a == 0] = np.nan

#calculating of the mean and conversion to degree celcius from digital numbers
in_pix_mean = (np.nanmean(in_pix_a, axis=0) * 0.00341802) + 149 - 273.15

rel_temp = in_pix_mean - out_avg

#conversion from dataarray to raster
in_xres = arcpy.GetRasterProperties_management(inside, "LEFT")

in_yres = arcpy.GetRasterProperties_management(inside, "BOTTOM")

in_x = in_xres.getOutput(0)

in_y = in_yres.getOutput(0)

#save relative temperature raster
in_result = arcpy.NumPyArrayToRaster (rel_temp, arcpy.Point(in_x, in_y), x_cell_size=30)

arcpy.management.DefineProjection (in_result, "PROJCS['ETRS89_UTM_zone_32N',GEOGCS['GCS_ETRS_1989',DATUM['D_ETRS_1989',SPHEROID['GRS_1980',6378137,298.257222101]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]],PROJECTION['Transverse_Mercator'],PARAMETER['latitude_of_origin',0],PARAMETER['central_meridian',9],PARAMETER['scale_factor',0.9996],PARAMETER['false_easting',500000],PARAMETER['false_northing',0],UNIT['Meter',1]]")

in_result.save(path+"/in"+str(len(years))+"JM_"+mean_year[2:]+"rel")

#save absolute temperature raster
in_abs = arcpy.NumPyArrayToRaster (in_pix_mean, arcpy.Point(in_x, in_y), x_cell_size=30)

arcpy.management.DefineProjection (in_abs, "PROJCS['ETRS89_UTM_zone_32N',GEOGCS['GCS_ETRS_1989',DATUM['D_ETRS_1989',SPHEROID['GRS_1980',6378137,298.257222101]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]],PROJECTION['Transverse_Mercator'],PARAMETER['latitude_of_origin',0],PARAMETER['central_meridian',9],PARAMETER['scale_factor',0.9996],PARAMETER['false_easting',500000],PARAMETER['false_northing',0],UNIT['Meter',1]]")

in_abs.save(path+"/in"+str(len(years))+"JM_"+mean_year[2:])



    





