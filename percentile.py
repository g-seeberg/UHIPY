# -*- coding: utf-8 -*-

import arcpy
import os
import numpy as np

"""
-----Define paths and parameters-----
"""

#define the working directory all files should be saved in 
wd = ""

#define warming spot percentile
warm = 98

#define cooling spots percentile
cool = 2

#temperature difference raster
deltatemp = ""
"""
----------------------
"""

arcpy.env.workspace = wd

arcpy.env.overwriteOutput=True

inRas = arcpy.Raster(deltatemp)

lowerLeft = arcpy.Point(inRas.extent.XMin,inRas.extent.YMin)

ras_np = arcpy.RasterToNumPyArray(inRas)

mask = ras_np != -3

per_95 = np.percentile(ras_np[mask], warm)

ras_per95 = ras_np

ras_per95[ras_per95 <= per_95] = np.nan

ar_95 = arcpy.NumPyArrayToRaster(ras_per95,lowerLeft,30)

arcpy.management.DefineProjection (ar_95, "PROJCS['ETRS89_UTM_zone_32N',GEOGCS['GCS_ETRS_1989',DATUM['D_ETRS_1989',SPHEROID['GRS_1980',6378137,298.257222101]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]],PROJECTION['Transverse_Mercator'],PARAMETER['latitude_of_origin',0],PARAMETER['central_meridian',9],PARAMETER['scale_factor',0.9996],PARAMETER['false_easting',500000],PARAMETER['false_northing',0],UNIT['Meter',1]]")

ar_95.save("r_d_"+int(warm)+"per.tif")

del ar_95


ras_np = arcpy.RasterToNumPyArray(inRas)

mask = ras_np != -3

per_5 = np.percentile(ras_np[mask], cool)

ras_per5 = ras_np

ras_per5[ras_per5 >= per_5] = np.nan

ar_5 = arcpy.NumPyArrayToRaster(ras_per5,lowerLeft,30)

arcpy.management.DefineProjection (ar_5, "PROJCS['ETRS89_UTM_zone_32N',GEOGCS['GCS_ETRS_1989',DATUM['D_ETRS_1989',SPHEROID['GRS_1980',6378137,298.257222101]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]],PROJECTION['Transverse_Mercator'],PARAMETER['latitude_of_origin',0],PARAMETER['central_meridian',9],PARAMETER['scale_factor',0.9996],PARAMETER['false_easting',500000],PARAMETER['false_northing',0],UNIT['Meter',1]]")

ar_5.save("r_d_"+int(warm)+"per.tif")

del ar_5

print("done")