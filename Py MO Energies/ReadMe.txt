Use the cclib python library to extract and plot MO energies as a level diagram.

Uses pycairo for plotting

The work is done in two stages
#1 ExtractMOEnergies.py reads one or more comp chem output files and writes out a CSV
#2 PlotMOEnergies.py reads the CSV and plots a diagram as PDF

Edit ExtractMOEnergies to determine which input files are used and to name the CSV

Each input file generates 5 columns of data (except the last which generates 4). The 1st 4 cols are: MO number, energy in eV, symmetry label, 0 or 1 to show occupancy (double or single occupancy is shown as 1).
The 5th column gives the MO number of the next set which is assumed to correlate.

Edit the CSV to change the titles, to remove MOs that should not be plotted and to change the correlation lines. Correlation defaults to energy-ordering. Enter 0 for correlation to omit that correlation line. An MO may be omitted by deleting either the line or the value in the first column.


Edit PlotMOEnergies to change the input file, output file, plot size, font sizes, whether to show correlations.
