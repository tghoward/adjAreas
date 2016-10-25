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
    input point layer has a field named "site_ID" and these are unique
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
# start with the sample points, buffer them
pointLoc = "D:/EPA_AdjArea/CalcAdjArea/NYW14_testPts.gdb"
pointLayer = "SitePoints"
inPoints = pointLoc + "/" + pointLayer

buffedPts = pointLoc + "/" + "SitePtsBuff1pt5km"
buffDist = "1500"
# do the buffer, don't merge the resulting polys
arcpy.Buffer_analysis(inPoints, buffedPts, buffDist, "FULL","ROUND","NONE")

#%%
# get a list of ObjectID, siteID tuples for all records, just to be sure for the next step
cursor = arcpy.SearchCursor(buffedPts)
idList = []
for row in cursor:
    idval = row.getValue("OBJECTID")
    siteval = row.getValue("site_ID")
    idList.append((idval,siteval))

siteList = [x[1] for x in idList]
if len(siteList) > len(set(siteList)):
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

for tup in idList:
    selStmt = "OBJECTID = " + str(tup[0])  #first value of tuple is objectid
    arcpy.SelectLayerByAttribute_management(lyr,"NEW_SELECTION", selStmt)
    siteID = tup[1]  #second value of tuple is siteid. Needs to be unique. TODO: test for that
    outname = outPath + "\\" + siteID + ".tif"
    extent = lyr.getSelectedExtent()
    ENV.extent = str(extent.XMin) + " " + str(extent.YMin) + " " + str(extent.XMax) + " " + str(extent.YMax)
    print "clipping " + siteID
    outExtractByMask = SA.ExtractByMask(inRas, lyr)
    outExtractByMask.save(outname)

arcpy.SelectLayerByAttribute_management(lyr, "CLEAR_SELECTION")

del lyr, selStmt
    
#%%
# complete Pit Remove for each disk

inPath = baseOutPath + "/disks_1_DEM"
outPath = baseOutPath + "/disks_2_pitsRemoved"

ENV.workspace = inPath
RasList = arcpy.ListRasters("*","TIF")

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
RasList = arcpy.ListRasters("*","TIF")

if not os.path.exists(outPath):
    os.makedirs(outPath)
if not os.path.exists(outPath2):
    os.makedirs(outPath2)
    
for ras in RasList:   
    lyrName = ras[:-7]
    outRas = outPath + "/" + lyrName + "_fd.tif"
    outRas2 = outPath2 + "/" + lyrName + "_sl.tif"
    arcpy.DinfFlowDir_TauDEM(ras, 8, outRas, outRas2)

#%%
# calculate contributing area for each disk and point
inPath = baseOutPath + "/disks_3_flowdir"
outPath = baseOutPath + "/disks_4b_contribArea"
outShp = baseOutPath + "/disks_4a_pointShps"

ENV.workspace = inPath
RasList = arcpy.ListRasters("*","TIF")

if not os.path.exists(outPath):
    os.makedirs(outPath)
if not os.path.exists(outShp):
    os.makedirs(outShp)

cursor = arcpy.SearchCursor(inPoints)
siteList = []
for row in cursor:
    site = row.getValue("site_ID")
    siteList.append(site)

#lyr = arcpy.mapping.Layer(inPoints)

pointLoc = "D:/EPA_AdjArea/CalcAdjArea/NYW14_testPts.gdb"
pointLayer = "SitePoints"
inPoints = pointLoc + "/" + pointLayer

arcpy.MakeFeatureLayer_management(inPoints, "lyr2")
for tup in idList:
    selStmt = "site_ID = '" + site + "'"
    selStmt = "OBJECTID = " + str(tup[0])
    site = tup[1]
    arcpy.SelectLayerByAttribute_management("lyr2","NEW_SELECTION", selStmt)
    outFileN = outShp + "/" + site + "_pt.shp"
    outFileN = outFileN.replace("-","_") #illegal character in shapefile name
    arcpy.CopyFeatures_management("lyr2", outFileN)

    
    
    
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
 

del lyr, cursor, row     
            
#%%
    
arcpy.GetCount_management('lyr2')
    