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

BASE_OUT_PATH = "D:/EPA_AdjArea/CalcAdjArea/output"

#%%
# get a list of siteIDs for all records; make sure they are unique
POINT_LOC = "D:/EPA_AdjArea/CalcAdjArea/inputs"
POINT_LAYER = "SitePoints_2.shp"
IN_POINTS = POINT_LOC + "/" + POINT_LAYER

cursor = arcpy.SearchCursor(IN_POINTS)
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
OUT_SHP = BASE_OUT_PATH + "/e_pts_pointShps"

if not os.path.exists(OUT_SHP):
    os.makedirs(OUT_SHP)

arcpy.MakeFeatureLayer_management(IN_POINTS, "lyr2")

for site in idList:
    selStmt = "site_ID = '" + site + "'"
    arcpy.SelectLayerByAttribute_management("lyr2", "NEW_SELECTION", selStmt)
    outFileN = OUT_SHP + "/" + site + "_pt.shp"
    outFileN = outFileN.replace("-", "_") #illegal character in shapefile name
    arcpy.CopyFeatures_management("lyr2", outFileN)

arcpy.SelectLayerByAttribute_management("lyr2", "CLEAR_SELECTION")
#%%
# expand the reach of each point.
# buffer the points by 50 m

IN_PATH = BASE_OUT_PATH + "/e_pts_pointShps"
OUT_PATH = BASE_OUT_PATH + "/f_pts_buff_pols"

if not os.path.exists(OUT_PATH):
    os.makedirs(OUT_PATH)

ENV.workspace = IN_PATH
shpList = arcpy.ListFeatureClasses()

for shp in shpList:
    site = shp[:-7]
    buffDist = "50"
    outShp = OUT_PATH + "/" + site + "_bu.shp"
    arcpy.Buffer_analysis(shp, outShp, buffDist, "FULL", "ROUND", "NONE")


#%%
# use a statewide constant raster (all values of 1)
# to make points for each cell within each polygon

IN_CONST_RAS = "D:/EPA_AdjArea/CalcAdjArea/inputs/constantRaster.tif"
IN_PATH = BASE_OUT_PATH + "/f_pts_buff_pols"
OUT_PATH = BASE_OUT_PATH + "/g_disks_buffPts"

if not os.path.exists(OUT_PATH):
    os.makedirs(OUT_PATH)

ENV.workspace = IN_PATH
shpList = arcpy.ListFeatureClasses()

ENV.cellSize = IN_CONST_RAS
ENV.snapRaster = IN_CONST_RAS

for shp in shpList:
    site = shp[:-7]
    shpFull = IN_PATH + "/" + shp
    ENV.extent = shpFull
    outRas = OUT_PATH + "/" + site + "_bp.tif"
    arcpy.PolygonToRaster_conversion(shpFull, "FID", outRas, "CELL_CENTER", "", 10)

arcpy.ClearEnvironment("extent")

IN_PATH = BASE_OUT_PATH + "/g_disks_buffPts"
OUT_PATH = BASE_OUT_PATH + "/h_pts_in_buff"

if not os.path.exists(OUT_PATH):
    os.makedirs(OUT_PATH)

ENV.workspace = IN_PATH
rasList = arcpy.ListRasters("*", "TIF")

for ras in rasList:
    site = ras[:-7]
    rasFull = IN_PATH + "/" + ras
    outShp = OUT_PATH + "/" + site + "_bp.shp"
    arcpy.RasterToPoint_conversion(rasFull, outShp, "VALUE")

#%%
# calculate contributing area for each disk and point
IN_PATH = BASE_OUT_PATH + "/c_disks_flowdir"
OUT_PATH = BASE_OUT_PATH + "/i_disks_contribArea"
IN_SHP = BASE_OUT_PATH + "/h_pts_in_buff"

if not os.path.exists(OUT_PATH):
    os.makedirs(OUT_PATH)

ENV.workspace = IN_PATH
RasList = arcpy.ListRasters("*", "TIF")

ENV.workspace = IN_SHP
shpList = arcpy.ListFeatureClasses()

for shp in shpList:
    site = shp[:-7].replace("_", "-").lower()
    for ras in RasList:
        rname = ras[:-7].lower()
        #print rname
        if rname == site:
            #print "...match"
            flowDirGrid = IN_PATH + "/" + ras
            outContribArea = OUT_PATH + "/" + rname + "_ca.tif"
            inShap = IN_SHP + "/" + shp
            arcpy.AreaDinf_TauDEM(flowDirGrid, inShap, "", "false", 8, outContribArea)
#%%

#print(arcpy.ListEnvironments())


