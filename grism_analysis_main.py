'''
grism_analysis_main

prototype edited Mar 27th 2022 - AS
last updated 2 Apr 2022 - WG

'''
from bin.grism_analysis_web import grism_web
from bin.grism_analysis_lib import grism_analysis
import os,glob
from datetime import date, timedelta, datetime
import astropy.io.fits as pyfits

def main():
    web_analyzer = grism_web()
    fits_image = web_analyzer.get_fits(web_analyzer) # Get initial fits image
    
    if not False: # TODO: Add advanced option on first page for entry of custom calibration file, otherwise search for one
        defaultDir = 'calibrations/'
        
        # Get date of image to iterate back to latest calibration file, parse header into date object
        im, hdr = pyfits.getdata(fits_image, 0, header=True)
        fitsDate = hdr['DATE-OBS']
        startDate = date(int(fitsDate[0:4]), int(fitsDate[5:7]), int(fitsDate[8:10]))
        
        # Iterate to find latest calib file in last 180 days
        for testDate in (startDate - timedelta(n) for n in range(180)):
            if os.path.isfile(defaultDir+'grism_cal_6_'+testDate.strftime('%Y_%m_%d')+'.csv'):
                cal_file = defaultDir+'grism_cal_6_'+testDate.strftime('%Y_%m_%d')+'.csv'
                break
            else: continue

    if not os.path.exists(cal_file):
        raise Exception('Calibration file not located!') # ? Is there a way to do popups instead of breaking?
    
    # ? Does this need to be done? The image isn't actually modified when it is being analyzed. 
    with open("temp.fts", "wb") as binary_file: # Write fits image to file so it can be analyzed
        binary_file.write(fits_image['content'])
    
    grism_analyzer = grism_analysis('temp.fts', cal_file) # instantiate analyzer with fits image and calibration file
    web_analyzer.run_analysis(web_analyzer, grism_analyzer)

if __name__ == '__main__':
    main()