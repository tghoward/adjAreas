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

ENV.workspace = "D:/EPA_AdjArea/CalcAdjArea/output/_wrkspace"
ENV.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")
arcpy.ImportToolbox("C:/Program Files/TauDEM/TauDEM5Arc/TauDEM Tools.tbx", "TauDEM")

baseOutPath = "D:/EPA_AdjArea/CalcAdjArea/output"

#%%
# get a list of siteIDs for all records; make sure they are unique
pointLoc = "D:/EPA_AdjArea/CalcAdjArea/inputs"
pointLayer = "SitePoints_2.shp"
inPoints = pointLoc + "/" + pointLayer

cursor = arcpy.SearchCursor(inPoints)
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
# split points into separate shapefiles as tauDEM can't seem to use selections
outShp = baseOutPath + "/disks_4a_pointShps"

if not os.path.exists(outShp):
    os.makedirs(outShp)

arcpy.MakeFeatureLayer_management(inPoints, "lyr2")

for site in idList:
    selStmt = "site_ID = '" + site + "'"
    arcpy.SelectLayerByAttribute_management("lyr2","NEW_SELECTION", selStmt)
    outFileN = outShp + "/" + site + "_pt.shp"
    outFileN = outFileN.replace("-","_") #illegal character in shapefile name
    arcpy.CopyFeatures_management("lyr2", outFileN)

arcpy.SelectLayerByAttribute_management("lyr2","CLEAR_SELECTION")

#%%   
# calculate contributing area for each disk and point
inPath = baseOutPath + "/disks_3_flowdir"
outPath = baseOutPath + "/disks_4b_contribArea"

if not os.path.exists(outPath):
    os.makedirs(outPath)

ENV.workspace = inPath
RasList = arcpy.ListRasters("*","TIF")
    
ENV.workspace = outShp
shpList = arcpy.ListFeatureClasses()    

for shp in shpList:
    site = shp[:-7].replace("_","-")
    for ras in RasList:
        rname = ras[:-7]
        #print rname
        if rname == site:
            #print "...match"
            flowDirGrid = inPath + "/" + ras
            outContribArea = outPath + "/" + rname + "_ca.tif"
            inShp = outShp + "/" + shp
            arcpy.AreaDinf_TauDEM(flowDirGrid, inShp, "", "false", 8, outContribArea)
 
#%%
    