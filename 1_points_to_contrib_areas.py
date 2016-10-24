# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 14:42:24 2016

@author: Tim Howard

This script begins with, as inputs:
    sampled wetland points
    10 m dem
It then extracts an area around each point and, through many steps, estimates the 
upland area contributing to that point (or a region around the point)

Assumptions:
    input point layer has a field named "site_ID"
"""

#%%
# setup
import os
import arcpy
from arcpy import env as ENV
import arcpy.sa as SA

ENV.workspace = "D:/EPA_AdjArea/CalcAdjArea"
ENV.overwriteOutput=True

arcpy.CheckOutExtension("Spatial")

arcpy.ImportToolbox("C:/Program Files/TauDEM/TauDEM5Arc/TauDEM Tools.tbx", "TauDEM")

#%%
# start with the sample points, buffer them
pointLoc = "D:/EPA_AdjArea/CalcAdjArea/NYW14_testPts.gdb"
pointLayer = "SitePoints"
inPoints = pointLoc + "/" + pointLayer

buffedPts = pointLoc + "/" + "SitePtsBuff1pt5km"
buffDist = "1500"
# do the buffer, don't merge the resulting polys
arcpy.Buffer_analysis(inPoints, buffedPts, buffDist, "FULL","ROUND","NONE")

#%%
# get a list of ObjectIDs for all records, just to be sure for the next step
cursor = arcpy.SearchCursor(buffedPts)
idList = []
for row in cursor:
    idval = row.getValue("OBJECTID")
    idList.append(idval)
    
#%%
# extract a separate DEM raster for each buffered point. Call them 'disks'
arcpy.MakeFeatureLayer_management(buffedPts, "lyr")

inRas = "D:/GIS_data/DEM/Masked_NED_Resampled_10m_DEM.tif"
outPath = "D:/EPA_AdjArea/CalcAdjArea/output/disks_1_DEM"

if not os.path.exists(outPath):
    os.makedirs(outPath)

for i in idList:
    selStmt = "OBJECTID = " + str(i)
    arcpy.SelectLayerByAttribute_management("lyr","NEW_SELECTION", selStmt)
    for row in arcpy.SearchCursor("lyr"):
        print row.site_ID
        outname = outPath + "\\" + row.site_ID + ".tif"
    outExtractByMask = SA.ExtractByMask(inRas, "lyr")
    outExtractByMask.save(outname)

## TODO: reduce the size of each raster here??  Right now they have the full extent of original?
    

#%%
# complete Pit Remove for each disk

inPath = outPath
ENV.workspace = inPath
RasList = arcpy.ListRasters("*","TIF")

outPath = "D:/EPA_AdjArea/CalcAdjArea/output/disks_2_pitsRemoved"
if not os.path.exists(outPath):
    os.makedirs(outPath)
    
for ras in RasList:
    lyrName = ras[:-4]
    outRas = outPath + "/" + lyrName + "_pr.tif"
    arcpy.PitRemove_TauDEM(ras, "", "", 8, outRas)

#%%    
# calculate flow direction (infinity) and slope for each disk

inPath = outPath
ENV.workspace = inPath
RasList = arcpy.ListRasters("*","TIF")

outPath = "D:/EPA_AdjArea/CalcAdjArea/output/disks_3_flowdir"
if not os.path.exists(outPath):
    os.makedirs(outPath)

outPath2 = "D:/EPA_AdjArea/CalcAdjArea/output/disks_3b_slope"
if not os.path.exists(outPath2):
    os.makedirs(outPath2)
    
for ras in RasList:   
    lyrName = ras[:-7]
    outRas = outPath + "/" + lyrName + "_fd.tif"
    outRas2 = outPath2 + "/" + lyrName + "_sl.tif"
    arcpy.DinfFlowDir_TauDEM(ras, 8, outRas, outRas2)

#%%
# calculate contributing area for each disk and point
inPath = outPath
ENV.workspace = inPath
RasList = arcpy.ListRasters("*","TIF")

outPath = "D:/EPA_AdjArea/CalcAdjArea/output/disks_4_contribArea"
if not os.path.exists(outPath):
    os.makedirs(outPath)

# get a list of records from the point layer
cursor = arcpy.SearchCursor(inPoints)
ptSites = []
for row in cursor:
    siteID = row.getValue("site_ID")
    ptSites.append(siteID)    
ptSites.sort()

for site in ptSites:
    for ras in RasList: 
        rname = ras[:-7]
        if site == rname:
            #do stuff here
            return

            
            
flowDirGrid = "D:\\EPA_AdjArea\\CalcAdjArea\\output\\nyw14-007"
OutContribAreaGrid = "D:\\EPA_AdjArea\\CalcAdjArea\\output\\nyw14-007-contrib"




arcpy.AreaDinf_TauDEM(flowDirGrid, inPointFC, "", "false", 8, OutContribAreaGrid)
    
    
    
#%%
    
    
    