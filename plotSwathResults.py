### SCRIPT TO READ IN AND PLOT SWATH PROFILER RESULTS
# Written by William Armstrong
# 23 July 2015

### USER DEFINED VARIABLES ###
folderPath = u'/Users/wiar9509/git/pySwath/'
shapeFilePath='swathOutputs/shapefiles/'
textFilePath='swathOutputs/textfiles/'
inPolySource='test9.shp' # initial shapefile filename used for swath profiler
#inRast='vv' # input raster filename from swath profiler
inRast='LC80640172013166LGN0_LC80640172014137LGN0_2013-334_336_20_69_hp_filt_3.0_vv.tif'
#inRast='LC80640172013166LGN0_LC80640172013214LGN0_2013-190_48_20_69_hp_filt_3.0_vv.tif'
#inRast='wrangells_gdem.tif'


###### LOADING MODULES ######

import os
os.chdir(folderPath)
import numpy as np
import matplotlib.pyplot as plt

from osgeo import ogr # modify code to just use ogr, not arcGIS
from osgeo import osr
	
###### PROCESSING ######

figureOutPath='swathOutputs/figures/' # filepath for figure outputs
rastSplit=inRast.split('_') # break up input raster string
masterImage=rastSplit[0]
slaveImage=rastSplit[1]

# Read in shapefiles
shapefile=folderPath+inPolySource
driver = ogr.GetDriverByName("ESRI Shapefile")
dataSource = driver.Open(shapefile, 0)
layer = dataSource.GetLayer()
crs = layer.GetSpatialRef() # Coordinate reference system

numLines=layer.GetFeatureCount() # Number of lines in shapefile

for line in range(numLines):

	# Initializing
	east=[]
	north=[]
	dist=[]
	min=[]
	mean=[]
	max=[]
	stdDev=[]
	
	trans=layer.GetFeature(line)
	transectName=trans.GetField(1)
	print 'Plotting '+transectName
	shapeName=transectName+'polygons.shp'
	
	# Opening layer to plot
	shapeDatasource = driver.Open(shapeFilePath+shapeName, update=0)
	shapeLayer = shapeDatasource.GetLayer()
	
	numBoxes = shapeLayer.GetFeatureCount()
	
	for box in range(numBoxes):
		boxNow=shapeLayer.GetFeature(box)
		if boxNow.GetField(5) is not None: # some are 'None'
			east.append(boxNow.GetField(1))
			north.append(boxNow.GetField(2))
			dist.append(boxNow.GetField(3))
			min.append(boxNow.GetField(4))
			mean.append(boxNow.GetField(5))
			max.append(boxNow.GetField(6))
			stdDev.append(boxNow.GetField(8))
			
	dist=np.array(dist)
	
	# Read in elevation profile
	zData=np.genfromtxt(folderPath+textFilePath+transectName+'_wrangells_gdem_stats.csv',delimiter=',',skip_header=1)
	
	zMin=[]
	zMean=[]
	zMax=[]
	
	zLen=len(zData)
	
	for cell in range(zLen):
		zMin.append(zData[cell][4])
		zMean.append(zData[cell][5])
		zMax.append(zData[cell][6])
	
	titleText=transectName+' over '+masterImage+' to '+slaveImage
	ax=plt.subplot(111)
	uLine=ax.plot(dist/1000,mean,color='k',linewidth=2,label='u$_{mean}$')
	ax.fill_between(dist/1000.0,min,max,color='gray',alpha=0.5,label='Range')
	ax.set_title(titleText,fontsize=18)
	ax.set_xlabel('Distance [km]',fontsize=14)
	ax.set_ylabel('Velocity [m d$^{-1}$]',fontsize=14)
	ax.set_ylim([0,2])
	ax2=ax.twinx()
	zLine=ax2.plot(dist/1000,zMean,color='b',linewidth=2,label='z$_{mean}$')
	ax2.set_ylabel('Elevation [m]',fontsize=14)
	
	# This combines legends
	lns = uLine+zLine
	labs = [l.get_label() for l in lns]
	ax.legend(lns, labs, loc=0)
	
	ax.grid()
	plt.savefig(figureOutPath+transectName+'_'+masterImage+'_'+slaveImage+'_profile.pdf',orientation='landscape',format='pdf')
	#plt.show()
	plt.draw()
	plt.close()