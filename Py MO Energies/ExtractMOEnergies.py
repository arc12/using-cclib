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
import os
import logging
from cclib.parser import ccopen

path="/home/arc1/gamess/Oxygen" #alt use ./
outFile="MO_Energies.csv"
files = ['A1-Opt_6-31G(d)_B3LYP_Singlet_RHF.log',
		 'A1-Opt_6-31G(d)_B3LYP_Singlet_UHF.log',
		 'A1-Opt_6-31G(d)_B3LYP_Triplet.log']

#to hold the data
energies = []
symmetries = []
occupied = []

#the number of MOs to be output. is the min no of MOs in the input files
nMOs = 1000

#read and extract
for f in files:
	print "Reading file: %s" % f
	qmRaw = ccopen(os.path.join(path, f))
	qmRaw.logger.setLevel(logging.ERROR) #reduce logging info
	qmParsed = qmRaw.parse()
	energies.append(qmParsed.moenergies[0])
	symmetries.append(qmParsed.mosyms[0])
	occupied.append(range(qmParsed.nmo)<=qmParsed.homos[0])
	if (qmParsed.nmo<nMOs):
		nMOs=qmParsed.nmo
		print "Will export %i MO energies" % nMOs

#write out as groups of columns as CSV
print "Writing out MO data to %s" % outFile
output = open(os.path.join(path,outFile), "w")

#group titles
for f in files:
	output.write("\"%s\",,,,," % f)
output.write("\n")#end the line

#data (MO index, energy, symmetry label, occupied T/F, correlate-with)
# "correlate-with" will just be the MO index. it may be changed in the CSV to show crossing correlations
for i in range(nMOs):
	for fi in range(len(files)):		
		output.write("%3i,%9.3f,%s,%i," % (i+1, energies[fi][i],symmetries[fi][i],occupied[fi][i]))
		if (fi<len(files)-1):
			output.write("%i," % (i+1))#correlates-with does not make sense on last group
	output.write("\n")#end the line
output.close()
