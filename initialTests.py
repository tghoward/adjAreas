# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 14:42:24 2016

@author: NYNHP_admin
"""

import arcpy as AP
from arcpy import env as E

E.workspace = "D:/EPA_AdjArea/CalcAdjArea"
E.overwriteOutput=True

# start with the sample points

pointLoc = "D:/EPA_AdjArea/CalcAdjArea/NYW14_testPts.gdb"
pointLayer = "SitePoints"
inPoints = pointLoc + "/" + pointLayer

outBuff = pointLoc + "/" + "SitePtsBuff1km"
buffDist = "1000"

AP.Buffer_analysis(inPoints, outBuff, buffDist, "FULL","ROUND","NONE")

