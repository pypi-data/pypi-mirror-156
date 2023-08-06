##################################################################################
### PURPOSE: Main calling function
##################################################################################

##################################################################################
### PURPOSE: Import Statements
##################################################################################
from matplotlib.backends.backend_pdf import PdfPages
import sys

try:
    from make_plot import plotting as plotting
except ImportError:
    from .make_plot import plotting as plotting
try:
    from utils import *
except ImportError:
    from .utils import *
from PIL import Image
import warnings


#supress all warnings from terminal
warnings.filterwarnings("ignore")




def output_figures(input_file, output_save_dir_plus_name):

    '''Main calling function

    Main function that calls other functions to find properties for the list of sources

    Args:
        input_file (str): Points to a list (.txt) with two columns (ra, dec) and 
            1 row per source with 1 header row
        output_save_dir_plus_name(str): The path and name for where the flipbook
            should be saved on user's computer

    Returns:
        None
    '''

    pp = PdfPages(output_save_dir_plus_name) #directory to save output flipbook to
    


    #Open the coordinates from the user file
    ras, decs = read_table(input_file)

    no_sources = len(ras)

    #Loop through the coordinates for the sources
    for idx, (r, d) in enumerate(zip(ras, decs)):


        source, temp, radius, lum = load_gaia(r, d)
        sdss_id = load_sdss(r, d)
        wave, flux = get_spectrum(r, d)
        days, norm_flux, _ = load_tess(r, d)


        #Call function to make plot
        temp_img = plotting(wave, flux, temp, lum, r, d, days, norm_flux)

        #Read plot in as image and save
        fig, ax = plt.subplots(figsize = (12, 8))

        im = Image.open(temp_img)

        ax.imshow(im)
        ax.set_xticks([])
        ax.set_yticks([])

        pp.savefig(fig)

        print("Done with: " + str(idx+1) + " out of " + str(no_sources) + " Sources")
    
    pp.close()



if __name__ == "__main__":
    input = str(sys.argv[1])
    output = str(sys.argv[2])
    output_figures(input, output)
