#!/usr/bin/env python
"""
Test . Various utilities
 -*- coding: UTF-8 -*-
"""

def getReelLimits(tubeDescription):
    (tube, strStart, strEnd) = tubeDescription.strip('\x00').split()
    (dummy, startReel) = strStart.split("=")
    (dummy, endReel) = strEnd.split("=")
    
    return float(startReel), float(endReel)

def getEtaPhiFromTube(tubeName):
    strHf, strEta, strPhi, strTower, dummy = tubeName.strip('\x00').split('_')
    
    hf = int(strHf.replace('HFP', ''))
    iEta = int(strEta.replace('ETA', ''))
    iPhi = int(strPhi.replace('PHI', ''))
    
    return hf, iEta, iPhi
    
def getMeanQie8(yy, xx, startBin = None):
    
    if startBin == None:
        startBin = 0
        
    wsum = 0
    tsum = 0
    for i in range(startBin, len(xx) - 1):
        tsum += yy[i]
        if i > 31:
            xBin = (xx[i-1] + xx[i-2])/2.
        else:
            xBin = (xx[i+1] + xx[i])/2.
        wsum += yy[i] * xBin
    
    if tsum >0.:
        wmean = wsum/tsum
    else:
        wmean = 0.
    
    return wmean

def getMeanQie10(yy, xx, startBin = None):
    
    if startBin == None:
        startBin = 0
        
    wsum = 0
    tsum = 0
    for i in range(startBin, len(xx) - 1):
        tsum += yy[i]
        xBin = (xx[i+1] + xx[i])/2.
        wsum += yy[i] * xBin
    
    if tsum >0.:
        wmean = wsum/tsum
    else:
        wmean = 0.
    
    return wmean
         
    