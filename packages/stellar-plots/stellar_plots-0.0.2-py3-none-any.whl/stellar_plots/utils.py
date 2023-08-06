##################################################################################
### IMPORT STATEMENTS
##################################################################################
import numpy as np
import pandas as pd
import lightkurve as lk
from astropy.io import fits
from astropy import units as u
from matplotlib import pyplot as plt
from astroquery.sdss import SDSS
from astroquery.gaia import Gaia
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import sys
'''
todo
- what if the input ra dec aren't in degrees
- (Isabella): handle case of wrong input file
'''

def read_table(fname):
    '''
    Read in stars from a file if it exists with columns RA & Dec.
    
    Args:
        fname (str): name of file that contains stars to read in.

    Returns:
        ra (array): right ascension (ra) values of input stars.
        dec (array): declination (dec) values of input stars.
    '''

    #ra, dec = np.loadtxt(fname, skiprows = 0, unpack = True, delimiter = ',')
    #return ra, dec
    df = pd.read_csv(fname, names=['ra','dec'], on_bad_lines='skip')
    return df['ra'].to_numpy(), df['dec'].to_numpy()
    

def load_gaia(ra, dec, dr=2):

    '''
    Read in Gaia data from Gaia DR2, and returns stellar parameters & Gaia IDs.

    Args:
        ra (float): ra values of input stars.
        dec (float): dec values of input stars.
        dr (int): Gaia data release no. Default is 2.

    Returns:
        gaia_id (int): Gaia Source IDs for all stars.
        teff (float): stellar effective temperature in Kelvin.
        rad (float): stellar radius in solar units.
        lum (float): stellar luminosity in solar units.
    '''

    if dr == 2:
        GAIA_CATALOG='I/345/gaia2'
    elif dr == 3:
        GAIA_CATALOG='I/355/gaiadr3'
    else:
        print('This GAIA version does not exist. Please specify either 2 or 3.')
        sys.exit()

    coord = SkyCoord(ra=ra, dec=dec, unit = (u.deg, u.deg))
    try:
        cat=Vizier.query_region(coord, catalog=GAIA_CATALOG, radius=2*u.arcsecond)
        cat=cat[0].to_pandas()
        return float(cat['Source'].to_numpy()), float(cat['Teff'].to_numpy()), float(cat['Rad'].to_numpy()), float(cat['Lum'].to_numpy())
    except:
        #print('Object with (RA,Dec)=(%s,%s) not found.'%(ra,dec))
        return np.nan, np.nan, np.nan, np.nan

def load_sdss(ra, dec):
    '''
    Read in Gaia data from Gaia DR2.

    Args:
        ra (float): ra of input stars.
        dec (float): dec of input stars.
    
    Returns:
        sdss_ids (array): SDSS ID of input star.
    '''

    SDSS_CATALOG='V/147/sdss12'

    coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg)
    try:
        cat=Vizier.query_region(coord, catalog=SDSS_CATALOG, radius=2*u.arcsecond)
        cat=cat[0].to_pandas().iloc[0]
        sdss_id= cat['SDSS12']
    except:
        #print('Object with (RA,Dec)=(%s,%s) not found.'%(ra,dec))
        sdss_id = np.nan
    return sdss_id

def load_kepler(ra, dec, quarters=False, cadence='long'):
    '''
    Load in photometry from Kepler if exists. Example: KIC 3733346 (287.11345099999994, 38.81283)

    Args:
        ra (float): ra values of input stars.
        dec (float): dec values of input stars.
        quarters (boolean): Kepler quarters to download. Default is False.
        cadence (str): Kepler cadence of data to use. Default is long.
    
    Returns:
        time (array): time values in lightcurve
        flux (array): flux values in lightcurve
        kicid (int): KICID of object
    '''
    coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg)
    if quarters:
        sr = lk.search_lightcurve(coord, author='Kepler', quarter=quarters, cadence=cadence)        
    else:    
        sr = lk.search_lightcurve(coord, author='Kepler', cadence=cadence)
    if len(sr) > 0:
        lcs=sr.download_all()
        lc = lc.stitch()
        lc = lc.normalize(unit='ppm').remove_nans().remove_outliers().flatten()
        kicid = int(sr[0].table['target_name'].value.data[0][4:])
        return lc.time.value, lc.flux.value, kicid
    else:
        return [np.nan],[np.nan],[np.nan]

def load_tess(ra, dec):
    '''
    Load in photometry from TESS if exists. Example: KIC 3733346 (287.11345099999994, 38.81283)
    TESS example: 261136679
    
    Args:
        ra (float): ra values of input stars.
        dec (float): dec values of input stars.

    Returns:
        time (array): time values in lightcurve
        flux (array): flux values in lightcurve
        ticid (int): TICID of object
    '''
    TICID = 261136679
    sr    = lk.search_targetpixelfile('TIC %s' % TICID)[0]
    if len(sr)>0:
        tpf = sr.download(quality_bitmask='default', author='SPOC')
        lc  = tpf.to_lightcurve()
        lc  = lc.normalize(unit='ppm').remove_nans().remove_outliers().flatten()
        return lc.time.value,lc.flux.value,tpf.targetid
    else: 
        #print('TIC %s not found.' % TICID)
        return np.nan, np.nan, np.nan
    

def get_spectrum(ra, dec):
    '''
    Returns the spectrum of input star from SDSS.

    Args:
        ra (float): ra of input stars.
        dec (float): dec of input stars.
    
    Returns:
        sp_lambda (array): wavelength in SDSS spectrum
        sp_flux (array): flux in SDSS spectrum
    '''

    coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg)

    try:
        sp = SDSS.get_spectra(coordinates = coord, radius=2*u.arcsec)[0][1]

        sp_data = sp.data

        sp_flux = sp_data.flux
        sp_lambda = 10**sp_data.loglam #lambda is returned in log space

    except(ValueError, RuntimeError, TypeError):
        return(-99, -99)

    return sp_lambda, sp_flux

