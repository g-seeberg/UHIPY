# -*- coding: utf-8 -*-
"""
-----IMPORTANT-----
All Satellite scenes are in the working directory folder with the path: 
    working directory\year\scene\band
e.g.:
    Working Directory\2004\LT05_L2SP_194026_20040723_20200903_02_T1\LT05_L2SP_194026_20040723_20200903_02_T1_QA_PIXEL.TIF
For different naming conventions code needs to be adjusted
-------------------
"""

import arcpy
import os


"""
-----Define paths and parameters-----
"""

#define the working directory all files should be saved in 
wd = ""

#define .txt with pixelvalues that indicate cloudcover (seperated by row)
cld_path = "tmp/cloudmask"

years =["2004", "2005", "2006", "2007", "2008", "2016", "2017", "2018", "2019", "2020"]

#define .shp of the buffer+city
area_shp = ""

#define .shp of the buffer
buffer_shp = ""

#define .shp of the city
city_shp = ""

"""
----------------------
"""

arcpy.env.workspace = wd

arcpy.env.overwriteOutput=True

os.chdir(wd)
        
if not os.path.exists(cld_path):
    os.makedirs(cld_path)

#directory in which the final mask will be stored
final_path = "masks"

if not os.path.exists(final_path):
    os.makedirs(final_path)

arcpy.management.Copy(buffer_shp, cld_path+"/merge2.shp")

f = open("cloudmask.txt")

cloudpx_str = [line for line in f.readlines()]
        
cloudpx_int = [int(i) for i in cloudpx_str]
    
f.close()

for year in years:
    
    s_path = wd+"/"+year
    
    scenes = os.listdir(s_path)
    
    #get dates from scenes YYYYMMDD
    ldate = [x.split('_')[3] for x in scenes]
    
    yr = year[2:]
    
    #list of dates converted to YYMMDD
    sdate = []
    
    for date in ldate:
       
        tmpdate = yr+date[4:]
    	
        sdate.append(tmpdate)
    
    z = 0
    
    #project and clip all scenes (clipped to city+buffer area, city area (in) and buffer area (out))
    for scene in scenes:
        
        b_path = wd+"/"+year+"/"+scene
        
        bands = os.listdir(b_path)
        
        tmp_path = wd+"/tmp/"+year
        
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
        
        band_i_want = scene+"_QA_PIXEL.TIF"
        
        print ("Project: "+sdate[z])
        
        in_tmp = year+"/"+scene+"/"+band_i_want
        
        out_tmp = tmp_path+"/"+sdate[z]+"4prj"
        
        arcpy.management.DefineProjection(in_tmp, "PROJCS['WGS_1984_UTM_Zone_32N',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137,298.257223563]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]],PROJECTION['Transverse_Mercator'],PARAMETER['latitude_of_origin',0],PARAMETER['central_meridian',9],PARAMETER['scale_factor',0.9996],PARAMETER['false_easting',500000],PARAMETER['false_northing',0],UNIT['Meter',1]]")
        
        arcpy.management.ProjectRaster(in_tmp, out_tmp, "PROJCS['ETRS89_UTM_zone_32N',GEOGCS['GCS_ETRS_1989',DATUM['D_ETRS_1989',SPHEROID['GRS_1980',6378137,298.257222101]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]],PROJECTION['Transverse_Mercator'],PARAMETER['latitude_of_origin',0],PARAMETER['central_meridian',9],PARAMETER['scale_factor',0.9996],PARAMETER['false_easting',500000],PARAMETER['false_northing',0],UNIT['Meter',1]]")
        
        print ("Clip all: "+sdate[z])
        
        in_tmp = tmp_path+"/"+sdate[z]+"4prj"
        
        out_tmp = tmp_path+"/"+sdate[z]+"4clip"
        
        arcpy.management.Clip(in_tmp, "", out_tmp, area_shp, "0", "ClippingGeometry")
        
        print ("To Polygon: "+sdate[z])
        
        in_raster = tmp_path+"/"+sdate[z]+"4clip"
        
        out_shape = cld_path+"/"+sdate[z]+"4.shp"
        
        arcpy.conversion.RasterToPolygon(in_raster, out_shape)
        
        print ("Clip inside: "+sdate[z])
        
        in_tmp = cld_path+"/"+sdate[z]+"4.shp"
        
        out_tmp = cld_path+"/"+sdate[z]+"4in.shp"
        
        arcpy.analysis.Clip(in_tmp, city_shp, out_tmp)
        
        print ("Clip outside: "+sdate[z])
        
        in_tmp = cld_path+"/"+sdate[z]+"4.shp"
        
        out_tmp = cld_path+"/"+sdate[z]+"4out.shp"
        
        arcpy.analysis.Clip(in_tmp, buffer_shp, out_tmp)
        
        z = z + 1

#list of all cloud shapefiles for the buffer area
out_shp = os.listdir(cld_path)

out_shp = [x for x in out_shp if "4out.shp" in x]

out_shp = [x for x in out_shp if not "xml" in x]

out_shp = [x for x in out_shp if not "lock" in x]

#combine all shapefiles into one cloudmask for the buffer area (saved under /masks and /tmp/cloudmask)
for shp in out_shp:
  
    print (shp)
    
    tmp = cld_path+"/"+shp
        
    tmp_cloud = "tmp_cloud"
        
    arcpy.MakeFeatureLayer_management(tmp, tmp_cloud)
        
    for number in cloudpx_str:
            
        arcpy.SelectLayerByAttribute_management(tmp_cloud, "ADD_TO_SELECTION", "gridcode ="+number)
            
    if int(arcpy.GetCount_management(tmp_cloud).getOutput(0)) > 0:
            
        arcpy.DeleteFeatures_management(tmp_cloud)
        
    arcpy.management.Copy(tmp, cld_path+"/tmp.shp")
        
    try:
            
        arcpy.analysis.Clip(cld_path+"/merge2.shp", cld_path+"/tmp.shp", cld_path+"/merge_tmp.shp")
            
    except:
            
        print ("Cloudcover: 100%")
        
    arcpy.management.Copy(cld_path+"/merge_tmp.shp", cld_path+"/merge2.shp")
        
    print ("done")
   
arcpy.management.Copy(cld_path+"/merge_tmp.shp", wd+"/masks/cldmsk.shp")

    