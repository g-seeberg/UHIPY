-----Documentation-----


This code was used for the paper "Evaluating the potential of Landsat satellite data to monitor the effectiveness of measures to mitigate urban heat islands: A case study for Stuttgart (Germany)". The paper is currently under review at Urban Science (mdpi).
RED, NIR, TIR and cloudmask(QA) bands from Landsat collection 2 must be available.  
Workingdirectory (wd) must be the same for all scripts.  
modules necessary: arcpy (with arcgis pro), os and numpy.  
Scripts must be executed in the given order.  
All scripts may need modification for the specific area of interest and other specifications.  

cloudmask.py:  
-takes the cloudmask(QA) band and calculates a mask with all clouds from all selected scenes  
-is necessary for main_script  
-saves cloudmask as shapefile as "masks/cldmsk.shp"  
  
main_script.py:  
-takes the satellite scenes from landsat collection 2 filters out the relevant bands (RED, NIR for NDVI and TIR)  
-applies all masks (cloudmask, urban mask, height mask)  
-converts digital numbers to temperature in celcius  
-calculates the mean temperature over the selected time period for every pixel  
-saves the average buffer temperature under "Xyear_average_YYYY.txt"   
-saves the average urban area absolute temperature raster under "inXJM_YY"  
-saves the relative temperature raster (urbantemp - buffertemp) under "inXJM_YYrel"  
-can only be done when all scenes are taken by one satellite (Landsat 5 or 8)  
-All satellite scenes must be in the working directory folder with the path:   
 working directory\year\scene\band  
-numpy array size must be adjusted to city and buffer area (line 286, 307 and 351)   

ndvi.py:  
-applies all masks  
-saves the averaged ndvi for every date and area in mean_ndvi.txt  
  
ndvi_xjm.py:  
-calculates the mean NDVI over the selected time period  
-saves raster files for the buffer (ndvi/ndvimeanYYout), city (ndvi/ndvimeanYYin) and urban area in the city (ndvi/ndvimeanYYurb)  
  
percentile.py:  
-filters out the pixels above and under a percentile  
-saves these pixels as raster under "r_d_percentile_per.tif"  
