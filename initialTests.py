# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 14:42:24 2016

@author: Tim Howard
"""

#%%
# setup
import arcpy
from arcpy import env as ENV
import arcpy.sa as SA

ENV.workspace = "D:/EPA_AdjArea/CalcAdjArea"
ENV.overwriteOutput=True

arcpy.CheckOutExtension("Spatial")

arcpy.ImportToolbox("C:\\Program Files\\TauDEM\\TauDEM5Arc\\TauDEM Tools.tbx", "TauDEM")

#%%
# start with the sample points, buffer them
pointLoc = "D:/EPA_AdjArea/CalcAdjArea/NYW14_testPts.gdb"
pointLayer = "SitePoints"
inPoints = pointLoc + "/" + pointLayer

buffedPts = pointLoc + "/" + "SitePtsBuff1km"
buffDist = "1000"

arcpy.Buffer_analysis(inPoints, buffedPts, buffDist, "FULL","ROUND","NONE")

#%%
# get a list of ObjectIDs for all records, just to be sure
cursor = arcpy.SearchCursor(buffedPts)
idList = []
for row in cursor:
    idval = row.getValue("OBJECTID")
    idList.append(idval)
    
#%%
# extract a separate raster for each buffered point
arcpy.MakeFeatureLayer_management(buffedPts, "lyr")

inRas = "D:/EPA_AdjArea/CalcAdjArea/tauDEMtests/flowdir.tif"
outPath = "D:\\EPA_AdjArea\\CalcAdjArea\\output"


for i in idList:
    selStmt = "OBJECTID = " + str(i)
    arcpy.SelectLayerByAttribute_management("lyr","NEW_SELECTION", selStmt)
    for row in arcpy.SearchCursor("lyr"):
        print row.site_ID
        outname = outPath + "\\" + row.site_ID
    outExtractByMask = SA.ExtractByMask(inRas, "lyr")
    outExtractByMask.save(outname)

#%%

flowDirGrid = "D:\\EPA_AdjArea\\CalcAdjArea\\output\\nyw14-007"
OutContribAreaGrid = "D:\\EPA_AdjArea\\CalcAdjArea\\output\\nyw14-007-contrib"
inPointFC = "D:\\EPA_AdjArea\\CalcAdjArea\\NYW14_testPts.gdb\\demToPoint_clip_ID"



arcpy.AreaDinf_TauDEM(flowDirGrid, inPointFC, "", "false", 8, OutContribAreaGrid)
    
    
    
#%%
    
    
    