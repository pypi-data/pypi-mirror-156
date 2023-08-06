# stellar_plots

A Python code used to generate descriptive plots of properties for a individual stars.
Accepts a list of coordinate (ra/dec) in degrees, of sources to plot.

The input file must be a comma separated list with two columns, ra and dec, and no header. 

The output produces a figure for each source in the list with subplots pulling data from SDSS, Gaia and Tess+Kepler and saves each figure as a single page in a PDF that is saved to the User's computer. 


## To run in Python:

```
from stellar_plots.driver import output_figures as main
main('/path/to/list/of/coordinates.csv', '/path/to/output/pdftosave.pdf')
```


## To run from the command line:

```
python -m stellar_plots.driver '/path/to/list/of/coordinates.csv' '/path/to/output/pdftosave.pdf'
```
