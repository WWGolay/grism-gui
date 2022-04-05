'''
grism_analysis_web

prototype updated last Mar 30th 2022
'''

import io
from pywebio.input import file_upload, input_group, NUMBER
from pywebio.output import put_text, put_image, use_scope, put_button, popup
from pywebio.pin import *
from pywebio import config,start_server
import pywebio.input as pywebio_input
import pywebio.pin as pywebio_pin
import io
from bin.grism_tools_lib import grism_tools
"""
Notes:
-Class uses the PywebIO persistent-input(PIN) functionality. Every input that alters graphs first sets the attribute, then
calls for the linked graphs to be updated.
-The use_scope method is used to place the graphs, this allows the webpage to keep all graphs in the same place when clearing
the sections and re-making the graphs. When calling these functions from the PIN module, it automatically passes the altered value
as a parameter, but this isn't useful (some plots use multiple parameters) so a dummy parameter is used
"""
class grism_web:
    def __init__(self):
        #self.plot_radio_dict = [ {'label':'Default', 'value':'def', 'selected':True},
        #    {'label':'Strip Image', 'value':'str'}, {'label':'2x2', 'value':'tbt'}  ]
        self.lines_checkbox_dict=[
            {'label':'Hydrogen (Balmer)', 'value':'H', 'selected':True},
            {'label':'Helium', 'value':'He'},
            {'label':'Carbon', 'value':'C'},
            {'label':'Nitrogen', 'value':'N'},
            {'label':'Oxygen', 'value':'O'}] # ? Can we add in calcium here?
        #Set default parameters for graphs.
        self.lines=['H']
        self.minWL = 380
        self.maxWL = 750
        self.medavg = 3
        self.temperature = 10000
        self.stripHeight = -1
        self.stripCenter = -1

    def resubmit_grism_image(self, img):
        with open('temp/temp.fts', 'wb') as binary_file: # Write fits image to file so it can be analyzed
            binary_file.write(img['content'])
        grism_analyzer = grism_tools('temp/temp.fts', self.analyzer.get_calib())
        self.run_analysis(self, grism_analyzer)

    def update_med_avg(self, med_avg):
        m = med_avg
        if(m is None):
            m=3
        if(med_avg%2 == 0):
            m -= 1
            pin.medavg = m 
        self.medavg = m

    def update_lower_wl(self, lower):
        self.minWL = lower
    
    def update_upper_wl(self, upper):
        self.maxWL = upper
        
    def update_lines(self, lines):
        self.lines = lines

    def update_mode(self, mode):
        self.mode = mode

    def update_strip_height(self, height):
        self.stripHeight = height

    def update_strip_center(self, center):
        self.stripCenter = center

    def update_temperature(self, temperature):
        self.temperature = temperature

    @use_scope('fits_section', clear=True)
    def update_fits(self, dummy="dummy"):
        if self.stripHeight != -1 and self.stripCenter != -1:
            popup("TODO: Applying Calibration")
            #fits_figure = self.analyzer.apply_calibration(None, self.stripHeight)
        fits_figure = self.analyzer.plot_image(figsize=(10,10), cmap='gray')    
        fits_buf = io.BytesIO()
        fits_figure.savefig(fits_buf)
        put_image(fits_buf.getvalue())

    @use_scope('strip_section', clear=True)
    def update_strip(self, dummy=None):
        strip_figure = self.analyzer.plot_strip(cmap='jet')
        strip_buf = io.BytesIO()
        strip_figure.savefig(strip_buf)
        put_image(strip_buf.getvalue())

    @use_scope('2b2_section', clear=True)
    def update_two_by_two(self, dummy=None):        
        tbt_figure = self.analyzer.plot_2x2(ref_file='', medavg=self.medavg, xlims =[self.minWL,self.maxWL])
        tbt_buff = io.BytesIO()
        tbt_figure.savefig(tbt_buff)
        put_image(tbt_buff.getvalue())                   

    @use_scope('spectrum_section', clear=True)
    def update_spectrum(self, dummy=None):   
        spectrum_figure = self.analyzer.plot_spectrum(calibrated = True, plot_lines = self.lines,title='', medavg = self.medavg)
        spectrum_buf = io.BytesIO()
        spectrum_figure.savefig(spectrum_buf)
        put_image(spectrum_buf.getvalue())

    @use_scope('gauss_section', clear=True)
    def update_gauss(self, dummy=None):
        gauss_figure, popt = self.analyzer.fit_gaussian(self.minWL,self.maxWL, emission = True)
        gauss_buf = io.BytesIO()
        gauss_figure.savefig(gauss_buf)
        put_image(gauss_buf.getvalue())

    @use_scope('rectified_section', clear = True)
    def update_rectified(self, dummy = None):
        rectified_figure = self.analyzer.plot_rectified_spectrum(self.temperature,wavemin=self.minWL,wavemax=self.maxWL)
        rectified_buff = io.BytesIO()
        rectified_figure.savefig(rectified_buff)
        put_image(rectified_buff.getvalue())        


    @config(title='Iowa Robotic Observatory Observing Planner',theme="dark") 
    def get_fits(self):
        fits_input = [
        pywebio_input.file_upload("Select a .fts file to analyze",name="fits", accept=".fts", required=True)#Fits image file select
        ]
        form_ans=input_group("Select a Fits image to analyze", fits_input)
        fits = form_ans['fits']
        return fits

    @config(title='Iowa Robotic Observatory Observing Planner',theme="dark") 
    def run_analysis(self, grism_analyzer):
        self.analyzer = grism_analyzer
        put_text("GRISM ANALYSIS")

        #Outputs that change multiple graphs
        pywebio_pin.put_input(label="Median Average", name = "medavg", type=NUMBER, placeholder=3)
        pywebio_pin.pin_on_change(name="medavg", onchange=self.update_med_avg)
        pywebio_pin.pin_on_change(name="medavg", onchange=self.update_fits)
        pywebio_pin.pin_on_change(name="medavg", onchange=self.update_spectrum)

        pywebio_pin.put_slider(label="Minimum Wavelength", name="minWL", value= self.minWL, min_value= 0, max_value = 1000, step = 1)#pin gauss options
        pywebio_pin.pin_on_change(name="minWL", onchange=self.update_lower_wl)
        pywebio_pin.pin_on_change(name="minWL", onchange=self.update_fits)
        pywebio_pin.pin_on_change(name="minWL", onchange=self.update_gauss)

        pywebio_pin.put_slider(label="Maximum Wavelength", name="maxWL", value= self.maxWL, min_value= 0, max_value = 1000, step = 1)
        pywebio_pin.pin_on_change(name="maxWL", onchange=self.update_upper_wl)
        pywebio_pin.pin_on_change(name="maxWL", onchange=self.update_fits)
        pywebio_pin.pin_on_change(name="maxWL", onchange=self.update_gauss)
        
        self.update_fits()#put fits image
        
        pywebio_pin.put_input(label="Manual Strip Height", name = "stripHeight", type=NUMBER)
        pywebio_pin.pin_on_change(name="stripHeight", onchange=self.update_strip_height)
        pywebio_pin.put_input(label="Manual Strip Center", name = "stripCenter", type=NUMBER)
        pywebio_pin.pin_on_change(name="stripCenter", onchange=self.update_strip_center)
        put_button("Execute Manual Strip Calibration", onclick=self.update_fits)
        
        self.update_strip()

        self.update_spectrum(self.lines)#put spectrum
        pywebio_pin.put_checkbox(label="Plot Lines", name="plotLines", options=self.lines_checkbox_dict)#pin spectrum options
        pywebio_pin.pin_on_change(name="plotLines", onchange=self.update_lines)
        pywebio_pin.pin_on_change(name="plotLines", onchange=self.update_spectrum)

        self.update_gauss()#put gauss

        self.update_two_by_two()

        self.update_rectified()
        pywebio_pin.put_input(label="Temperature (K)", name = "temper", type=NUMBER, placeholder=10000)
        pywebio_pin.pin_on_change(name="temper", onchange=self.update_temperature)
        pywebio_pin.pin_on_change(name="temper", onchange=self.update_rectified)

        #put file input at the bottom that runs the analysis again (also to keep the form active)
        img = pywebio_input.file_upload("Select Another Fits Image For Analysis:", accept=".fts")
        self.resubmit_grism_image(img)
        