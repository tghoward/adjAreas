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
    site_ID values MUST NOT have hyphens "-". These are illegal in shapefile names
    (you can replace hyphens with underscore using field calculator in Arc, 
    using the re python library and Python as parser: add "import re" in Codeblock, then 
    re.sub("-", "_", !theSiteIDFieldWithHyphens!)
    in main code field.)

If running a new set of points and you want to keep earlier runs, move all the folders
in output/ to a new folder (except _workspace)

"""

#%%
# setup
import arcpy
from arcpy import env as ENV

ENV.workspace = "D:/EPA_AdjArea/CalcAdjArea/output/_wrkspace"
ENV.overwriteOutput = True
#arcpy.CheckOutExtension("Spatial")
#arcpy.ImportToolbox("C:/Program Files/TauDEM/TauDEM5Arc/TauDEM Tools.tbx", "TauDEM")

#%%
# start with the sample points, buffer them
POINT_LOC = "D:/EPA_AdjArea/CalcAdjArea/inputs"
POINT_LAYER = "all_points_4April2018.shp"
#POINT_LAYER = "ALL_GENPTS_CA_BC_MM_SP_AdjArea_7June2017.shp"
IN_POINTS = POINT_LOC + "/" + POINT_LAYER

BUFFERED_PTS = POINT_LOC + "/" + "AllPts_Buff1km.shp"
BUFF_DIST = "1000"
# do the buffer, don't merge the resulting polys
arcpy.Buffer_analysis(IN_POINTS, BUFFERED_PTS, BUFF_DIST, "FULL", "ROUND", "NONE")

#%%

#==============================================================================
# The previous call, Buffer_analysis, seems to create a situation in inPoints
# that messes up later attempts to use the same shapefile. Probably a bug. So this
# script needs to be stopped here and the next script run with a fresh console.
#==============================================================================
