# -*- coding: utf-8 -*-

import arcpy
import os
import pandas as pd

"""
-----Define paths and parameters-----
"""

#define the working directory all files should be saved in 
wd = ""

#shp of city+buffer
clip_shp = ""

#shp of city
in_shp = ""

#shp of buffer
out_shp =""

#calculated by cloudmask.py
cloudmask_out = ""

#shp of urban mask 
urban = ""

#ididvidually stored cloudmasks by cloudmask.py
cld_path = "tmp/cloudmask"

#define .txt with pixelvalues that indicate cloudcover (seperated by row)
f = open("cloudmask.txt")

#define all years included in the analysis
years =["2004", "2005", "2006", "2007", "2008", "2016", "2017", "2018", "2019", "2020"]

"""
----------------------
"""



arcpy.env.workspace = wd

arcpy.env.overwriteOutput=True

os.chdir(wd)
        
cloudpx_str = [line for line in f.readlines()]
        
cloudpx_int = [int(i) for i in cloudpx_str]
    
f.close()

results = pd.DataFrame(columns=["date", "all", "buffer", "city", "urban city"])

for year in years:
    
    scenes = os.listdir("ndvi/"+year)
    scenes = [x for x in scenes if "1clip" in x]
    scenes = [x for x in scenes if not "aux" in x]
    scenes = [x for x in scenes if not "ovr" in x]
    scenes = [x for x in scenes if not "lock" in x]
    
    sdate = []
    
    for scene in scenes:
       
        tmpdate = scene[:6]
    	
        sdate.append(tmpdate)
    
    #Calculate NDVI for each scene
    
    for date in sdate:
        
        red = arcpy.Raster("ndvi/"+year+"/"+date+"1clip")
        
        nir = arcpy.Raster("ndvi/"+year+"/"+date+"2clip")
        
        NDVI = (nir-red)/(nir+red)
        
        NDVI.save("ndvi/"+year+"/"+date+"ndvi")
        
    for date in sdate:
        
        print ("Cloudmask: "+date)
        
        in_tmp = "ndvi/"+year+"/"+date+"ndvi"
        
        out_tmp = "ndvi/"+year+"/"+date+"ndviin"
        
        masked = "ndvi/"+year+"/"+date+"ndviout"
        
        out_urb = "ndvi/"+year+"/"+date+"ndviurb"
        
        #cloud detection band
        cld_shape = cld_path+"/"+date+"4in.shp"
        
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
            
            arcpy.management.Clip(in_tmp, "", masked, cloudmask_out, "0", "ClippingGeometry")
            
            print ("--done")
            
        print ("urban mask")
        
        arcpy.management.Clip(out_tmp, "", out_urb, urban, "0", "ClippingGeometry")
        
        buffer_city_r = arcpy.GetRasterProperties_management(in_tmp, "MEAN")
        
        buffer_city = buffer_city_r.getOutput(0)
        
        city_r = arcpy.GetRasterProperties_management(out_tmp, "MEAN")
        
        city = city_r.getOutput(0)
        
        buffer_r = arcpy.GetRasterProperties_management(masked, "MEAN")
        
        buffer = buffer_r.getOutput(0)
        
        in_urb_r = arcpy.GetRasterProperties_management(out_urb, "MEAN")
        
        in_urb = in_urb_r.getOutput(0)
        
        d = date [4:6]+"."+date[2:4]+".20"+date[:2]
        
        means = pd.DataFrame([[d, buffer_city, buffer, city, in_urb]], columns=["date", "all", "buffer", "city", "urban city"])
        
        results = results.append(means)

results.to_csv("mean_ndvi.txt")
     
    
    
    
    