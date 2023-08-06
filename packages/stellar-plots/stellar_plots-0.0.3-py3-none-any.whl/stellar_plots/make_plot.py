##################################################################################
### PURPOSE: Plot the actual output for each source
##################################################################################


##################################################################################
### IMPORT STATEMENTS
##################################################################################
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import io
import math




##################################################################################
### PLOTTING FUNCTION
##################################################################################
def plotting(wave, flux, teff, logg, ra, dec, days, norm_flux):
    '''Plotting

    Make a figure with subplots for each of the data products pulled

    Args: 
        wave  (arr):   Numpy array. The wavelength values for the spectrum from SDSS.
        flux  (arr):   Numpy array. The flux values for the spectrum with SDSS.
        teff (float):  Float. The effective temperature from Gaia.
        lum  (float):  Float. The luminosity from Gaia. 
        ra   (float):  Float. Right Ascension of target.
        dec  (float):  Float. Declination of target.
        z    (float):  Float. Redshift of source.

    Returns:
        fig (Figure object) 
    '''


    fig = plt.figure(figsize = (10, 8))
    G = gridspec.GridSpec(20, 4)
    G.update(wspace=0.5, hspace=2.5) #include whitespace around plots

    ax1 = fig.add_subplot(G[10:14,:]) #spectrum
    ax1 = fig.axes[0]
    ax2 = fig.add_subplot(G[:8,0:2]) #HRD
    ax2 = fig.axes[1]
    ax3 = fig.add_subplot(G[:8,2:4]) #info
    ax3 = fig.axes[2]
    ax4 = fig.add_subplot(G[16:, :])
    ax4 = fig.axes[3]



    ### Spectrum
    ax1.set_xlabel(r'$\rm{Wavelength \ [\AA]}$', fontsize = 14)
    ax1.set_ylabel(r'$\mathrm{Normalized Flux}$', fontsize = 14)
    if not isinstance(wave, (np.ndarray, list, set,) ): #handle case of no available data
        ax1.set_ylim(0, 10)
        ax1.set_xlim(0, 100)
        ax1.annotate('No Spectrum Available', (25, 4), xytext = (25, 4), fontsize = 20)
    else:
        flux = [f/max(flux) for f in flux] #normalize flux for plotting
        ax1.plot(wave, flux, lw = 2, color = 'k')


    ### Light Curve
    ax4.set_xlabel(r'$\rm{Time [Days]}$', fontsize = 14)
    ax4.set_ylabel(r'$\mathrm{Normalized Flux}$', fontsize = 14)
    if not isinstance(days, (np.ndarray, list, set,) ): #handle case of no available data
        ax4.set_ylim(0, 10)
        ax4.set_xlim(0, 100)
        ax4.annotate('No Light Curve Available', (25, 4), xytext = (25, 4), fontsize = 20)
    else:
        ax4.plot(days, norm_flux, lw = 2, color = 'k')




    ### HR Diagram 
    ax2.set_xlabel(r'$\rm{T_\mathrm{eff} \ [K]}$', fontsize = 14)
    ax2.set_ylabel(r'$\mathrm{Log(g) \ [dex]}$', fontsize = 14)

    if teff < 0 or math.isnan(teff) == True or math.isnan(logg) == True: #handle case of no available data
        ax2.set_ylim(0, 10)
        ax2.set_xlim(0, 100)
        ax2.annotate('No HR Data Available', (3, 5), xytext = (3, 5), fontsize = 20)
    else:
        ax2.scatter(teff, logg, color = 'red', marker = 's', zorder = 1E6)

        #Plot the HR background of full Gaia Datasource
        full_t, full_g = np.loadtxt('./data/full_hr.txt', skiprows = 1, unpack = True)
        ax2.scatter(full_t, full_g, color = 'gray', s = 2)
        ax2.invert_xaxis()

    


    ### Info
    ax3.set_xticks([])
    ax3.set_yticks([])
    ax3.set_ylim(0, 100)
    ax3.set_xlim(0, 100)
    ax3.annotate(r"$\bf{Quick Stats: }$", (2, 90), xytext = (2, 90), fontsize = 14, color = 'k')
    ax3.annotate("Ra:  " + str(ra), (2, 80), xytext = (2, 80), fontsize = 14, color = 'k')
    ax3.annotate("Dec: " + str(dec), (2, 70), xytext = (2, 70), fontsize = 14, color = 'k')

    
    #Make a temporary file to hold the plot in
    temp = io.BytesIO()
    plt.savefig(temp, format="png")
    temp.seek(0)
    
    return temp



    