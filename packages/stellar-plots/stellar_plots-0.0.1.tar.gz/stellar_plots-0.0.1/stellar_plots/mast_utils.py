
import os, sys, re, json, time
import requests
import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord, Angle
from astroquery.vizier import Vizier
from astroquery.mast import Catalogs
from astropy.table import Table, Column, Row
from astropy.wcs import WCS

from urllib.parse import quote as urlencode
from urllib.request import urlretrieve
import http.client as httplib


def mastQuery(request):
    """Sends a request to the MAST server.
    Parameters
    ----------
    request : str
        JSON string for request.
    Returns
    ----------
    head :
        Retrieved data headers from MAST.
    content :
        Retrieved data contents from MAST.
    """
    server = 'mast.stsci.edu'

    # Grab Python Version
    version = '.'.join(map(str, sys.version_info[:3]))
        # Create Http Header Variables
    headers = {'Content-type': 'application/x-www-form-urlencoded',
               'Accept': 'text/plain',
               'User-agent': 'python-requests/'+version}
    # Encoding the request as a json string
    requestString = urlencode(json.dumps(request))
    # Opening the https cnnection
    conn = httplib.HTTPSConnection(server)
    # Making the query
    conn.request('POST', '/api/v0/invoke', 'request='+requestString, headers)

    # Getting the response
    resp = conn.getresponse()
    head = resp.getheaders()
    content = resp.read().decode('utf-8')

    # Close the https connection
    conn.close()

    return head, content

def crossmatch_by_position(pos, r, service):
    """Crossmatches [RA,Dec] position to a source in the Gaia DR2 or TIC catalog.
    Parameters
    ----------
    pos : tuple
        (RA, Dec)
    r :  float
        Radius of search for crossmatch.
    service : str
        Name of service to use. 'Mast.GaiaDR2.Crossmatch'
            or 'Mast.Tic.Crossmatch' are accepted.
    Returns
    -------
    table : astropy.table.Table
        Table of crossmatch results.
    """

    crossmatchInput = {'fields': [{'name':'ra' , 'type':'float'},
                                  {'name':'dec', 'type':'float'}],
                       'data': [{'ra':pos[0], 'dec':pos[1]}]}
    request = {'service':service,
               'data':crossmatchInput,
               'params': {'raColumn':'ra', 'decColumn':'dec', 'radius':r},
               'format':'json', 'removecache':True}
    headers, outString = mastQuery(request)
    return jsonTable(json.loads(outString))

def crossmatch_distance(pos, match):
    """Returns distance in arcsec between two sets of coordinates."""
    c1 = SkyCoord(pos[0]*u.deg, pos[1]*u.deg, frame='icrs')
    c2 = SkyCoord(match[0]*u.deg, match[1]*u.deg, frame='icrs')
    return c1.separation(c2).to(u.arcsec)

def jsonTable(jsonObj):
    """Converts JSON return type object into an astropy Table.
    Parameters
    ----------
    jsonObj :
        Output data from `mastQuery`.
    Returns
    ----------
    dataTable : astropy.table.Table
    """
    dataTable = Table()
    for col,atype in [(x['name'],x['type']) for x in jsonObj['fields']]:
        if atype=='string':
            atype='str'
        if atype=='boolean':
            atype='bool'
        if atype=='int':
            atype='float'
        dataTable[col] = np.array([x.get(col,None) for x in jsonObj['data']],dtype=atype)
    return dataTable

def tic_from_coords(coords):
    """Returns TIC ID, Tmag, and separation of best match(es) to input coords."""
    tess = crossmatch_by_position(coords, 0.01, 'Mast.Tic.Crossmatch')
    tessPos = [tess['MatchRa'], tess['MatchDEC']]
    sepTess = crossmatch_distance(coords, tessPos)
    subTess = tess[sepTess==np.min(sepTess)]
    return int(subTess['MatchID'].data[0]), [subTess['Tmag'].data[0]], sepTess[sepTess==np.min(sepTess)]/u.arcsec, int(subTess['version'][0]), subTess['contratio'].data[0]


def gaia_from_coords(coords):
    """Returns Gaia ID of best match(es) to input coords."""
    gaia = crossmatch_by_position(coords, 0.01, 'Mast.GaiaDR2.Crossmatch')
    gaiaPos = [gaia['MatchRA'], gaia['MatchDEC']]
    sepGaia = crossmatch_distance(coords, gaiaPos)
    return int(gaia[sepGaia==np.min(sepGaia)]['MatchID'].data[0])