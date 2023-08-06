from .xydata import xydata
from .reference import reference
from .pl import pl

import matplotlib.pyplot as plt
from datetime import date

class raman(xydata, reference):
    datatype = '.txt'
    imgformat = '.bmp'
    def __init__(self, rawdatafile, material, wavelength):
        xydata.__init__(self, rawdatafile+raman.datatype, quantity = ['Raman Shift', 'cm$^{-1}$', 'Intensity', 'a.u.'], title='Raman spectra', fig=[20, '#e6f0f8'])
        reference.__init__(self, material, 'raman', update=True)
        
        self.rawdatafile = rawdatafile
        self.img = plt.imread(rawdatafile+raman.imgformat)
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
    
    def to_pl(self):
        self.data['wl'] = 1/(1/self.wavelength - self.data['x']*1e-7)
        data = self.data[['wl', 'y']]
        filename = self.rawdatafile +'_pl'
        data.to_csv(filename+'.txt', header=None, index=None, sep='\t')
        plt.imsave(filename+self.imgformat, self.img)
        return pl(filename, self.sheet, self.wavelength)
        
        
    

