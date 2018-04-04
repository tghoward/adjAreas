# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 09:04:22 2016

@author: NYNHP_admin
"""
#%%
# setup
import os
import arcpy
from arcpy import env as ENV
from arcpy import sa as SA

ENV.workspace = "D:/EPA_AdjArea/CalcAdjArea/output/_wrkspace"
ENV.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

BASE_OUT_PATH = "D:/EPA_AdjArea/CalcAdjArea/output"

#%%

# first convert rasters to integer with all cells (! NoData cells) equal to 1

IN_PATH = BASE_OUT_PATH + "/i_disks_contribArea"
OUT_PATH = BASE_OUT_PATH + "/j_disks_contrib_int"

if not os.path.exists(OUT_PATH):
    os.makedirs(OUT_PATH)

print "cleaning up contrib area raster"    
    
ENV.workspace = IN_PATH
RasList = arcpy.ListRasters("*", "TIF")

for ras in RasList:
    lyrName = ras[:-7]
    print lyrName
    inRas = IN_PATH + "/" + ras
    outRas = OUT_PATH + "/" + lyrName + "_ci.tif" #contributing area integer
    result = SA.Int((arcpy.Raster(inRas) * 0) + 1)
    result.save(outRas)

#%%
# now convert to poly

IN_PATH = BASE_OUT_PATH + "/j_disks_contrib_int"
OUT_PATH = BASE_OUT_PATH + "/k_pols_contribArea"

if not os.path.exists(OUT_PATH):
    os.makedirs(OUT_PATH)

print "converting to polygon"
    
ENV.workspace = IN_PATH
RasList = arcpy.ListRasters("*", "TIF")

for ras in RasList:
    lyrName = ras[:-7].replace("-", "_")
    print " .. " + ras
    inRas = IN_PATH + "/" + ras
    outPol = OUT_PATH + "/" + lyrName + "_ca.shp" #contributing area
    arcpy.RasterToPolygon_conversion(inRas, outPol, "NO_SIMPLIFY", "VALUE")


#%%
# to clip these polys down to size, we first need to make another set of
# circles to use as clippers

IN_PATH = BASE_OUT_PATH + "/e_pts_pointShps"
OUT_PATH = BASE_OUT_PATH + "/l_pts_buff_pols540"

if not os.path.exists(OUT_PATH):
    os.makedirs(OUT_PATH)

print "clipping polys down to size"    
    
ENV.workspace = IN_PATH
shpList = arcpy.ListFeatureClasses()

for shp in shpList:
    site = shp[:-7]
    buffDist = "540"
    outShp = OUT_PATH + "/" + site + "_bu.shp"
    arcpy.Buffer_analysis(shp, outShp, buffDist, "FULL", "ROUND", "NONE")

IN_PATH = BASE_OUT_PATH + "/k_pols_contribArea"
CLIP_PATH = BASE_OUT_PATH + "/l_pts_buff_pols540"
OUT_PATH = BASE_OUT_PATH + "/m_clip_contribArea"

if not os.path.exists(OUT_PATH):
    os.makedirs(OUT_PATH)

ENV.workspace = IN_PATH
shpList = arcpy.ListFeatureClasses()

for shp in shpList:
    site = shp[:-7]
    print site
    inShp = IN_PATH + "/" + shp
    clpShp = CLIP_PATH + "/" + site.upper() + "_bu.shp"
    outShp = OUT_PATH + "/" + site + "_cr.shp" #contributing area restricted
    arcpy.Clip_analysis(inShp, clpShp, outShp)
    
#%%
# merge all the polys into one GDB

IN_PATH = BASE_OUT_PATH + "/m_clip_contribArea"
OUT_PATH = BASE_OUT_PATH + "/N_merge_up"
OUT_GDB = "clip_contribArea_FCs.gdb"
OUT_FC = OUT_PATH + "/" + OUT_GDB + "/contributingAreas"

if not os.path.exists(OUT_PATH):
    os.makedirs(OUT_PATH)
    
print "merge up to a single feature class"

ENV.workspace = IN_PATH
shpList = arcpy.ListFeatureClasses()

# first add a site_ID field to all of them
for shp in shpList:
    site = shp[:-7]
    arcpy.AddField_management(shp, "site_ID", "TEXT")
    cur = arcpy.UpdateCursor(shp)
    print "adding to attribute table for " + shp
    for row in cur:
        row.setValue("site_ID", site)
        cur.updateRow(row)

arcpy.CreateFileGDB_management(OUT_PATH, OUT_GDB)

arcpy.Merge_management(shpList, OUT_FC)

    