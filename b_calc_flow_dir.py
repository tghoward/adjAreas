# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 14:42:24 2016

@author: Tim Howard

This script begins with, as inputs:
    - sampled wetland points and buffered polygons (see prev script)
    - 10 m dem or other dem such as from lidar. Use 'mosaic to new raster' tool in 
      arcgis toolbox to create a single raster from many tiles. 
    - you can provide a dem that does not cover the full extent of the points. Those
      locations with no dem under them will be tossed. 

It then extracts an area around each point and, through many steps, estimates the
    upland area contributing to that point (or a region around the point)

Assumptions:
    input point layer has a field named "site_ID" and these are unique

If running straight from previous script,
    restart the kernal with ctrl+. in console (control period).
"""

#%%
# setup
import os
import arcpy
from arcpy import env as ENV
import arcpy.sa as SA

ENV.workspace = "D:/EPA_AdjArea/CalcAdjArea/output/_wrkspace"
ENV.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")
arcpy.ImportToolbox("C:/Program Files/TauDEM/TauDEM5Arc/TauDEM Tools.tbx", "TauDEM")

BASE_OUT_PATH = "D:/EPA_AdjArea/CalcAdjArea/output"

#%%
# get a list of siteIDs for all records, just to be sure for the next step
POINT_LOC = "D:/EPA_AdjArea/CalcAdjArea/inputs"
BUFFERED_PTS = POINT_LOC + "/" + "AdjArea_June2017_Buff1km.shp"

cursor = arcpy.SearchCursor(BUFFERED_PTS)
idList = []
for row in cursor:
    siteval = row.getValue("site_ID")
    idList.append(siteval)

#siteList = [x[1] for x in idList]
#if len(siteList) > len(set(siteList)):
if len(idList) > len(set(idList)):
    print "site_ID VALUES ARE NOT UNIQUE!!"
else:
    print "Values in site_ID column are unique"

# check if there are hyphens in idList
if True in ["-" in x for x in idList]:
    print "HYPHEN in site names! Remove them before proceeding"
else:
    print "No hyphens found; continue"

del cursor, row

#%%
# extract a separate DEM raster for each buffered point. Call them 'disks'
#arcpy.MakeFeatureLayer_management(buffedPts, "lyr")
lyr = arcpy.mapping.Layer(BUFFERED_PTS)

IN_RAS = "D:/GIS_data/DEM/Masked_NED_Resampled_10m_DEM.tif"
#IN_RAS = "D:/GIS_data/lidar_dem/MonroeCo_2mMosaic/MonroeMosaic2m.img"
#IN_RAS = "D:/GIS_data/lidar_dem/All_1m_mosaicDS/All_lidar_DEM_Mosaic.gdb/NYS_Lidar_DEM"

OUT_PATH = BASE_OUT_PATH + "/a_disks_DEM"

if not os.path.exists(OUT_PATH):
    os.makedirs(OUT_PATH)

for site in idList:
    #selStmt = "OBJECTID = " + str(tup[0])  #first value of tuple is objectid
    selStmt = "site_ID = '" + site + "'"
    arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", selStmt)
    #siteID = tup[1]  #second value of tuple is siteid. Needs to be unique.
    outname = OUT_PATH + "\\" + site + ".tif"
    extent = lyr.getSelectedExtent()
    XMIN = str(extent.XMin)
    YMIN = str(extent.YMin)
    XMAX = str(extent.XMax)
    YMAX = str(extent.YMax)
    ENV.extent = XMIN + " " + YMIN + " " + XMAX + " " + YMAX
    print "clipping " + site
    outExtractByMask = SA.ExtractByMask(IN_RAS, lyr)
    # if the result is all no data (e.g. no dem under the poly), don't save
    # careful: this keeps partial disks
    if arcpy.GetRasterProperties_management(outExtractByMask, "ALLNODATA").getOutput(0) == '0':
        print " ... saving " + site
        outExtractByMask.save(outname)
    else:
        print " ... " + site + " dem is all null"

arcpy.SelectLayerByAttribute_management(lyr, "CLEAR_SELECTION")

del lyr, selStmt
#%%
# reduce vertical resolution of DEM to remove micro-topography
# TRIAL!!

######## restart console here #####

#IN_PATH = BASE_OUT_PATH + "/a_disks_DEM"
#OUT_PATH = BASE_OUT_PATH + "/a_disks_DEM_zSmooth"
#
#ENV.workspace = IN_PATH
#RasList = arcpy.ListRasters("*","TIF")
#
#if not os.path.exists(OUT_PATH):
#    os.makedirs(OUT_PATH)
#
#for ras in RasList:
#    lyrName = ras[:-4]
#    outRas = OUT_PATH + "/" + lyrName + "_zs.tif" #z-direction smoothed
#    inras = SA.Raster(ras)
#    #result = SA.Float(SA.Int(inras * 10))/10
#    result = SA.Float(SA.Int(inras))
#    result.save(outRas)
######## restart console here #####

#%%
# complete Pit Remove for each disk

#IN_PATH = BASE_OUT_PATH + "/a_disks_DEM_zSmooth"
IN_PATH = BASE_OUT_PATH + "/a_disks_DEM"
OUT_PATH = BASE_OUT_PATH + "/b_disks_pitsRemoved"

ENV.workspace = IN_PATH
RasList = arcpy.ListRasters("*", "TIF")

if not os.path.exists(OUT_PATH):
    os.makedirs(OUT_PATH)

for ras in RasList:
    lyrName = ras[:-4]
    outRas = OUT_PATH + "/" + lyrName + "_pr.tif"
    print "pit removal on " + lyrName
    arcpy.PitRemove_TauDEM(ras, "", "", 8, outRas)

#%%
# calculate flow direction (infinity) and slope for each disk

IN_PATH = BASE_OUT_PATH + "/b_disks_pitsRemoved"
OUT_PATH = BASE_OUT_PATH + "/c_disks_flowdir"
OUT_PATH2 = BASE_OUT_PATH + "/d_disks_slope"

ENV.workspace = IN_PATH
RasList = arcpy.ListRasters("*", "TIF")

if not os.path.exists(OUT_PATH):
    os.makedirs(OUT_PATH)
if not os.path.exists(OUT_PATH2):
    os.makedirs(OUT_PATH2)

for ras in RasList:
    lyrName = ras[:-7]
    OUT_RAS = OUT_PATH + "/" + lyrName + "_fd.tif"
    OUT_RAS2 = OUT_PATH2 + "/" + lyrName + "_sl.tif"
    print "flow direction on " + lyrName
    arcpy.DinfFlowDir_TauDEM(ras, 8, OUT_RAS, OUT_RAS2)
