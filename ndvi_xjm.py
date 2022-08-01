# -*- coding: utf-8 -*-

import arcpy
import os
import numpy as np

"""
-----Define paths and parameters-----
"""

#define the working directory all files should be saved in 
wd = ""

#define years of selected time period
years = ["2016", "2017", "2018", "2019", "2020"]

"""
----------------------
"""




arcpy.env.workspace = wd

arcpy.env.overwriteOutput=True

os.chdir(wd)

mean_year = years[round((len(years))/2)]

ex = os.listdir("ndvi/"+years[0])

ex = [x for x in ex if "ndvi" in x]
    
ex = [x for x in ex if not "aux" in x if not "ovr" in x if not "lock" in x]

endings = ["in", "out", "urb"]

for ending in endings:

    l = [x for x in ex if ending in x]
    
    col = arcpy.GetRasterProperties_management("ndvi/"+years[0]+"/"+l[0], "COLUMNCOUNT").getOutput(0)
    
    row = arcpy.GetRasterProperties_management("ndvi/"+years[0]+"/"+l[0], "ROWCOUNT").getOutput(0)
    
    base_array = np.empty((2, int(row), int(col)))
    
    for year in years:
        
        scenes = os.listdir("ndvi/"+year)
        
        scenes = [x for x in scenes if "ndvi" in x]
        
        scenes = [x for x in scenes if not "aux" in x if not "ovr" in x if not "lock" in x]
        
        sdate = []
        
        for scene in scenes:
           
            tmpdate = scene[:6]
        	
            sdate.append(tmpdate)
        
        sdate = list(dict.fromkeys(sdate))
            
        for date in sdate:
            
            data = wd+"/ndvi/"+year+"/"+date+"ndvi"+ending
            
            ra_to_ar = arcpy.RasterToNumPyArray(data)
            
            array = np.empty ((int(row), int(col)))
            
            stack = np.stack((array, ra_to_ar))
        
            base_array = np.append(base_array, stack, axis=0)
            
       
    base_array[base_array == 0] = np.nan
    
    mean = (np.nanmean(base_array, axis=0))
    
    x = arcpy.GetRasterProperties_management("ndvi/"+years[0]+"/"+l[0], "LEFT").getOutput(0)
    
    y = arcpy.GetRasterProperties_management("ndvi/"+years[0]+"/"+l[0], "BOTTOM").getOutput(0)
    
    result = arcpy.NumPyArrayToRaster (mean, arcpy.Point(x, y), x_cell_size=30)
    
    arcpy.management.DefineProjection (result, "PROJCS['ETRS89_UTM_zone_32N',GEOGCS['GCS_ETRS_1989',DATUM['D_ETRS_1989',SPHEROID['GRS_1980',6378137,298.257222101]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]],PROJECTION['Transverse_Mercator'],PARAMETER['latitude_of_origin',0],PARAMETER['central_meridian',9],PARAMETER['scale_factor',0.9996],PARAMETER['false_easting',500000],PARAMETER['false_northing',0],UNIT['Meter',1]]")
    
    result.save("ndvi/"+"ndvimean"+mean_year[2:]+ending)
    

        
        
    
    