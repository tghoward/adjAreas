# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 14:42:24 2016

@author: NYNHP_admin
"""

#%%
# setup
import arcpy
from arcpy import env as E
import arcpy.sa as SA

E.workspace = "D:/EPA_AdjArea/CalcAdjArea"
E.overwriteOutput=True

arcpy.CheckOutExtension("Spatial")

#%%

# start with the sample points
pointLoc = "D:/EPA_AdjArea/CalcAdjArea/NYW14_testPts.gdb"
pointLayer = "SitePoints"
inPoints = pointLoc + "/" + pointLayer

outBuff = pointLoc + "/" + "SitePtsBuff1km"
buffDist = "1000"

arcpy.Buffer_analysis(inPoints, outBuff, buffDist, "FULL","ROUND","NONE")

#%%
# get a list of ObjectIDs for all records, just to be sure
cursor = arcpy.SearchCursor(outBuff)
idList = []
for row in cursor:
    idval = row.getValue("OBJECTID")
    idList.append(idval)
    
#%%


arcpy.MakeFeatureLayer_management(outBuff, "lyr")

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
need to use MakeFeatureLayer_management
and then Select layer by attribute or something 

inRas = "D:/EPA_AdjArea/CalcAdjArea/tauDEMtests/flowdir.tif"
outPath = "D:\\EPA_AdjArea\\CalcAdjArea\\output"

cursor = arcpy.SearchCursor(outBuff)
for row in cursor:
    polName = row.getValue("site_ID")
    print(polName)
    outExtractByMask = SA.ExtractByMask(inRas, row)
    outname = outPath + "\\" + polName
    outExtractByMask.save(outname)
    
    
    
    
#%%
    
    
#row = cursor.next()
#while row:
    