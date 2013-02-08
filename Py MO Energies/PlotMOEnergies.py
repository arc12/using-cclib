#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  untitled.py
#  
#  Copyright 2013 Adam Cooper <arc1@arc1-r700>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

#Uses pycairo
import cairo # import the Python module
import os
import csv
import math
#from array import *

path="/home/arc1/gamess/Oxygen" #alt use ./
inFile="MO_Energies.csv"
outFile="MO_Energies.pdf"

# canvas size
WIDTH=1000
HEIGHT=1000

# plotting size parameters
MARGIN=30 # indent of frame for actual plotting
LEVEL_WID=50 # width of an energy level line
SYMM_FONT=8 #font size for symmetry labels
GROUP_FONT=12 #font size for MO group (set) titles

#plotting options
DO_CORR=True #whether to show correlation lines. True or 1 for "yes", False or 0 for "no"

#to hold the data
moNumber=[]#MO index number
energies = []
symmetries = []
occupied = []
correlates = []
minEnergy=1000.0
maxEnergy=-1000.0

#read in the data to plot
csvfile = open(os.path.join(path,inFile), 'rb')
moData = csv.reader(csvfile, delimiter=',', quotechar='\"')
#titles in 1st row
titlesRow=moData.next()
numGroups = int((len(titlesRow)+1)/5)
print "%i groups of MOs found in %s" % (numGroups, inFile)
#extract and compose the data in a useful form, finding min/max energies
dataRow = moData.next()
while(dataRow):
	#only process if left-most cell is non-empty. This allows the user to simply hide energy levels by editing the CSV
	if(dataRow[0]):
		numberRow=[]
		energyRow=[]
		symmetryRow=[]
		occRow=[]
		corrRow=[]
		for g in range(numGroups):
			groupOffset=g*5
			numberRow.append(dataRow[groupOffset])
			en=float(dataRow[1+groupOffset])
			energyRow.append(en)
			symmetryRow.append(dataRow[2+groupOffset])
			occRow.append(dataRow[3+groupOffset])
			if(g<(numGroups-1)):
				corrRow.append(dataRow[4+groupOffset])
			minEnergy=min(minEnergy,en)
			maxEnergy=max(maxEnergy,en)
		moNumber.append(numberRow)
		energies.append(energyRow)
		symmetries.append(symmetryRow)
		occupied.append(occRow)
		correlates.append(corrRow)
	dataRow = next(moData,0)
	
#calculate transformations from data "coordinates" to plot coordinates
#the plot area is indented by a margin all round
plotWidth=WIDTH-2*MARGIN
plotHeight=HEIGHT-2*MARGIN
#the x positions of the centrelines of the energy level stacks
xSpacing=int(plotWidth/(numGroups+1))
xCentres=[]
for g in range(numGroups):
	xCentres.append(MARGIN + (g+1)*xSpacing)
#work out a coarse scaling. this equates to a tick-line interval
print("Energy min=%9.3f, max=%9.3f" % (minEnergy,maxEnergy))
yTick = math.pow(10,int(math.log10((maxEnergy-minEnergy)/2)))
#the energy offset and scaling
yMin=yTick*(math.floor(minEnergy/yTick))#these are the energy values at the margin:plot-area boundary
yMax=yTick*(math.ceil(maxEnergy/yTick))
print("Y tick interval=%9.3f, giving axis limits of (%9.3f,%9.3f)" % (yTick,yMin,yMax))
yScale=plotHeight/(yMax-yMin)

# setup a place to draw
surface = cairo.PDFSurface(os.path.join(path,outFile),WIDTH,HEIGHT)
ctx = cairo.Context (surface)

#draw plotting box
ctx.set_source_rgb(0,0,0)#black
ctx.rectangle(MARGIN,MARGIN,plotWidth,plotHeight)
ctx.stroke()

#draw set/group titles
ctx.select_font_face('Sans')
ctx.set_font_size(GROUP_FONT)
fascent, fdescent, fheight, fxadvance, fyadvance = ctx.font_extents()
y=MARGIN-fdescent-2 #font descenders should not quite touch the plot area box
for g in range(numGroups):
	txt=titlesRow[g*5]
	xbearing, ybearing, width, height, xadvance, yadvance = (
                    ctx.text_extents(txt))
	x=xCentres[g]-width/2
	ctx.move_to(x,y)
	ctx.set_source_rgb(0,0,0)
	ctx.show_text(txt)

#draw eV units, 0eV line and 10eV tick marks
#keeps same settings as group titles
#but make zero line be thin pale
ctx.set_line_width(1.0)
ctx.move_to(MARGIN,HEIGHT-MARGIN+int(yScale*yMin))
ctx.set_source_rgb(0.8,0.8,0.8)
ctx.rel_line_to(plotWidth,0)
ctx.stroke()
#thin black tick marks with values
ctx.set_source_rgb(0,0,0)
y=yMin
while(y<yMax):
	#tick
	yt=HEIGHT-MARGIN - int(yScale*(y-yMin))
	ctx.move_to(MARGIN,yt)
	ctx.rel_line_to(-3,0)
	ctx.stroke()
	#val
	if(yTick<1):
		"%g" % y
	else:
		txt=str(int(y))
	xbearing, ybearing, width, height, xadvance, yadvance = (
                    ctx.text_extents(txt))
	ctx.move_to(MARGIN-width-4,yt)
	ctx.show_text(txt)
	#next tick
	y+=yTick
#units
txt="eV"
xbearing, ybearing, width, height, xadvance, yadvance = (
                   ctx.text_extents(txt))
ctx.move_to(MARGIN-width-4,MARGIN)
ctx.show_text(txt)
	
#draw the energy levels and symmetry labels
ctx.set_line_width(1.0)
ctx.set_font_size(SYMM_FONT)
for i in range(len(energies)):
	for g in range(numGroups):
		#line
		x0=xCentres[g]-LEVEL_WID/2 #LHS of level line
		y0= HEIGHT-MARGIN - int(yScale*(energies[i][g]-yMin)) #LHS of energy line
		if(occupied[i][g]=='1'):
			ctx.set_source_rgb(0,0,1.0)#blue for occ levels
		else:
			ctx.set_source_rgb(0,1.0,0)#green for non-occ levels
		ctx.move_to(x0,y0)
		ctx.rel_line_to(LEVEL_WID,0)
		ctx.stroke()
		#correlation. 
		if(DO_CORR and (g<(numGroups-1))):
			corr_with=int(correlates[i][g])#this is the MO number, NOT a list index!
			if(corr_with>0): #a zero value  means no correlation
				corr_index=0
				#search for the correlated MO. Done like this because we have nested lists
				for j in range(len(moNumber)):
					if (int(moNumber[j][g+1]) == corr_with):
						corr_index=j
						break
				xc=xCentres[g+1]-LEVEL_WID/2
				yc= HEIGHT-MARGIN - int(yScale*(energies[corr_index][g+1]-yMin))
				ctx.set_source_rgb(0.7,0.7,1.0)#pale blue
				ctx.move_to(x0+LEVEL_WID+2,y0)
				ctx.line_to(xc-2,yc)
				ctx.stroke()
		#symm
		txt='{0}: {1}'.format(moNumber[i][g],symmetries[i][g])
		xbearing, ybearing, width, height, xadvance, yadvance = (
                    ctx.text_extents(txt))
		x=x0-width-2
		ctx.set_source_rgb(1,0,0)#red for symm labels
		ctx.move_to(x,y0)
		ctx.show_text(txt)
 
# finish up
ctx.stroke() # commit to surface
surface.finish()

# to do:
# - add y ticks and scale
