from .xydata import xydata
from .reference import reference

import matplotlib.pyplot as plt

from datetime import date

class pl(xydata, reference):
    datatype = '.txt'
    imgformat = '.bmp'
    def __init__(self, rawdatafile, material, wavelength):
        xydata.__init__(self, rawdatafile+pl.datatype, quantity = ['Wavelength', 'nm', 'Intensity', 'a.u.'], title='Photoluminescence', fig=[20, '#e6f0f8'])
        reference.__init__(self, material, 'pl', update=True)
        
        self.img = plt.imread(rawdatafile+pl.imgformat)
        self.wavelength = wavelength
        
        # Get reference peaks (use the same wavelength
        refs = reference.all_records()
        refs = refs[refs['excitation']==wavelength]
        self.refpeaks = refs[['material', 'code', 'label','cen', 'morphology']] 
        
        # plot the image and the full spectrum
        plt.clf()
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(self.fig[0],0.2*self.fig[0]), gridspec_kw={'width_ratios': [1, 3.5]}, constrained_layout=True)
        ax1.imshow(self.img)
        ax1.title.set_text("Sample image")
        ax2.set_yticklabels('')
        self.plot(ax=ax2, title = "Full Spectra")
        plt.show();
    
    def to_ev(self):
        if self.quantity[0]=='Wavelength':
            self.quantity = ['Photon energy', 'nm', 'Intensity', 'a.u.']
            self.data['x'] = 1239.8/self.data['x']
            self.xlabel = self.quantity[0] + ' (' + self.quantity[1] + ')'
            self.ylabel = self.quantity[2] + ' (' + self.quantity[3] + ')'
        self.plot()
        
    def to_nm(self):
        if self.quantity[0]=='Photon energy':
            self.quantity = ['Wavelength', 'nm', 'Intensity', 'a.u.']
            self.data['x'] = 1239.8/self.data['x']
            self.xlabel = self.quantity[0] + ' (' + self.quantity[1] + ')'
            self.ylabel = self.quantity[2] + ' (' + self.quantity[3] + ')'
        self.plot()
        