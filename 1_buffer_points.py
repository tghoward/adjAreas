# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 14:42:24 2016

@author: Tim Howard

This script begins with, as inputs:
    sampled wetland points

and then buffers each point a specified distance (1 or 1.5 km seems appropriate)
without merging the resulting polygons (important)

Assumptions:
    input point layer has a field named "site_ID" and these are unique
"""

#%%
# setup
import arcpy
from arcpy import env as ENV

ENV.workspace = "D:/EPA_AdjArea/CalcAdjArea/output/_wrkspace"
ENV.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")
arcpy.ImportToolbox("C:/Program Files/TauDEM/TauDEM5Arc/TauDEM Tools.tbx", "TauDEM")

baseOutPath = "D:/EPA_AdjArea/CalcAdjArea/output"

#%%
# start with the sample points, buffer them
pointLoc = "D:/EPA_AdjArea/CalcAdjArea/inputs"
pointLayer = "SitePoints_2.shp"
inPoints = pointLoc + "/" + pointLayer

buffedPts = pointLoc + "/" + "SitePtsBuff1pt5km.shp"
buffDist = "1500"
# do the buffer, don't merge the resulting polys
arcpy.Buffer_analysis(inPoints, buffedPts, buffDist, "FULL", "ROUND", "NONE")

#%%

#==============================================================================
# The previous call, Buffer_analysis, seems to create a situation in inPoints
# that messes up later attempts to use the same shapefile. Probably a bug. So this
# script needs to be stopped here and the next script run with a fresh console.
#==============================================================================
