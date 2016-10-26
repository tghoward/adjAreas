# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 14:42:24 2016

@author: Tim Howard

This script begins with, as inputs:
    sampled wetland points and buffered polygons (see prev script)
    10 m dem
It then extracts an area around each point and, through many steps, estimates the
upland area contributing to that point (or a region around the point)

Assumptions:
    input point layer has a field named "site_ID" and these are unique

If running straight from previous script, restart the kernal with ctrl+. in console.
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

baseOutPath = "D:/EPA_AdjArea/CalcAdjArea/output"

#%%
# get a list of ObjectID, siteID tuples for all records, just to be sure for the next step
pointLoc = "D:/EPA_AdjArea/CalcAdjArea/inputs"
buffedPts = pointLoc + "/" + "SitePtsBuff1pt5km.shp"

cursor = arcpy.SearchCursor(buffedPts)
idList = []
for row in cursor:
    siteval = row.getValue("site_ID")
    idList.append(siteval)

#siteList = [x[1] for x in idList]
#if len(siteList) > len(set(siteList)):
if len(idList) > len(set(idList)):
    print "site_ID VALUES ARE NOT UNIQUE!!"
else:
    print "values in site_ID column are unique"

del cursor, row

#%%
# extract a separate DEM raster for each buffered point. Call them 'disks'
#arcpy.MakeFeatureLayer_management(buffedPts, "lyr")
lyr = arcpy.mapping.Layer(buffedPts)

inRas = "D:/GIS_data/DEM/Masked_NED_Resampled_10m_DEM.tif"
outPath = baseOutPath + "/disks_1_DEM"

if not os.path.exists(outPath):
    os.makedirs(outPath)

for site in idList:
    #selStmt = "OBJECTID = " + str(tup[0])  #first value of tuple is objectid
    selStmt = "site_ID = '" + site + "'"
    arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", selStmt)
    #siteID = tup[1]  #second value of tuple is siteid. Needs to be unique. TODO: test for that
    outname = outPath + "\\" + site + ".tif"
    extent = lyr.getSelectedExtent()
    ENV.extent = str(extent.XMin) + " " + str(extent.YMin) + " " + str(extent.XMax) + " " + str(extent.YMax)
    print "clipping " + site
    outExtractByMask = SA.ExtractByMask(inRas, lyr)
    outExtractByMask.save(outname)

arcpy.SelectLayerByAttribute_management(lyr, "CLEAR_SELECTION")

del lyr, selStmt

#%%
# complete Pit Remove for each disk

inPath = baseOutPath + "/disks_1_DEM"
outPath = baseOutPath + "/disks_2_pitsRemoved"

ENV.workspace = inPath
RasList = arcpy.ListRasters("*", "TIF")

if not os.path.exists(outPath):
    os.makedirs(outPath)

for ras in RasList:
    lyrName = ras[:-4]
    outRas = outPath + "/" + lyrName + "_pr.tif"
    arcpy.PitRemove_TauDEM(ras, "", "", 8, outRas)

#%%
# calculate flow direction (infinity) and slope for each disk

inPath = baseOutPath + "/disks_2_pitsRemoved"
outPath = baseOutPath + "/disks_3_flowdir"
outPath2 = baseOutPath + "/disks_3b_slope"

ENV.workspace = inPath
RasList = arcpy.ListRasters("*", "TIF")

if not os.path.exists(outPath):
    os.makedirs(outPath)
if not os.path.exists(outPath2):
    os.makedirs(outPath2)

for ras in RasList:
    lyrName = ras[:-7]
    outRas = outPath + "/" + lyrName + "_fd.tif"
    outRas2 = outPath2 + "/" + lyrName + "_sl.tif"
    arcpy.DinfFlowDir_TauDEM(ras, 8, outRas, outRas2)

