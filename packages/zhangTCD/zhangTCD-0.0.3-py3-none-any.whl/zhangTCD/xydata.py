import pandas as pd
import numpy as np

from scipy.optimize import curve_fit
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.signal import find_peaks

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import seaborn as sns

import pkg_resources
import sys
import subprocess

from IPython.display import HTML, Latex, display, clear_output
import ipywidgets as widgets

required = {'SciencePlots'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed
if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
    
# pip install SciencePlots 
plt.style.use(['science', 'notebook', 'grid'])



class xydata():
    # initiate 2-dimensional xydata
    def __init__(self, rawdatafile, quantity=None, fig=None, title=None, legend =None):
        """
        rawdatafile is a txt file
        quntity = ['xlabel', 'xunit', 'ylabel', 'yunit'] if not provided ['x', 'a.u.', 'y', 'a.u.']
        fig = [xscale, 'background color'] if not provided [20, '#e6f0f8']
        title is the name of the data, it is the filename if not provided.
        legend is the legend in the figure, it is the filename if not provided.
        """
        # Import the txt file save it as pandas DataFrame in self.data
        self.data = pd.read_csv(rawdatafile, delimiter = "\t", names=['x', 'y'])
        
        # By default, the error is defined as sqrt(y); initialise smoothed as the raw and baseline as o
        self.data['err'] = np.sqrt(self.data.y)
        self.data['als'] = self.data['y']
        self.data['sm'] = self.data['y']
        self.data['bl'] = self.data['y']-self.data['y']
        
        # Define the variables 
        self.quantity = ['x', 'a.u.', 'y', 'a.u.'] if quantity is None else quantity 
        self.legend = rawdatafile if legend is None else legend
        self.title = rawdatafile if title is None else title
        self.fig = [18, '#e6f0f8'] if fig is None else fig
        self.xlabel = self.quantity[0] + ' (' + self.quantity[1] + ')'
        self.ylabel = self.quantity[2] + ' (' + self.quantity[3] + ')' 
        
        # Define baseline, smooth and find_peak paras
        self.bl_para = [10, 0, 15] # lam = 10, p = 0, niter = 15
        self.sm_para = [10, 1, 1]  # lam = 10, p = 1, niter = 1
        self.fp_para = [max(self.data['y'])/500, 1, (max(self.data['y'])-min(self.data['y']))/200, 1] # height, threshold, prominence, width
        
        # initialise the peaks array
        self.peaks = pd.DataFrame(columns=['code', 'label', 'cen', 'wid', 'amp'])
        self.peaks = self.peaks.fillna(0)
        self.tmp_peaks = pd.DataFrame(columns=['code', 'label', 'cen', 'wid', 'amp'])
        self.tmp_peakfit = {'label': 'tmp', 'cen': 0, 'wid':0, 'amp':0, 'xfit': None, 'yfit':None, 'pcov':None}
        # tmp values for searching peaks, avoid searching when manually assigning peaks
        self.tmpfitpeaks = []
        self.tmpfitpara = []
        self.manu_peaks = pd.DataFrame(columns=['code', 'label', 'cen', 'wid', 'amp'])
        #reference peaks
        self.refpeaks = pd.DataFrame(columns=['code', 'label', 'cen'])

 
        
    # Smoother - asymmetric least square
    def als(self, lam=1, p=0.5, niter=20):
        """
        WHITTAKER-EILERS SMOOTHER in Python 3 using numpy and scipy based on the work by Eilers [1].
        [1] P. H. C. Eilers, "A perfect smoother", Anal. Chem. 2003, (75), 3631-3636
        
        lam: parameter for the smoothing algorithm (roughness penalty), The larger, the smoother the data.
        p = 0, take y < z 
        niter = 1 for smoothing curve; p=0 and niter >10 to get the baseline;
        """
        y = self.data['y']
        L = len(y)
        D = sparse.csc_matrix(np.diff(np.eye(L), 2))
        w = np.ones(L)
        for i in range(niter):
            W = sparse.spdiags(w, 0, L, L)
            Z = W + lam * D.dot(D.transpose())
            z = spsolve(Z, w*y)
            w = p * (y > z) + (1-p) * (y < z)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(self.fig[0],0.4*self.fig[0]), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
        plt.subplots_adjust(wspace=0, hspace=0)
        ax1.scatter(self.data['x'], self.data['y'], s=5, color='red')
        yrange = ax1.get_ylim()
        ax1.plot(self.data['x'], z)
        ax1.set_ylim(yrange)
        ax2.scatter(self.data['x'], z-self.data['y'], s=2,color = 'grey')
        ax2.set_ylim([-max(self.data['y'])/2, max(self.data['y'])/2])
        self.data['als'] = z
    
    
    # Smooth the experimental curve
    def smooth_baseline(self):
        """
        Use widgets to tune the als algorithm for smoothing and baseline
        """
        print('Extract baseline and smooth data using the Asymmetric Least Square Algorithm:')
        
        #scroll bars for lambda, p, and number of iteration
        sl_lam = widgets.FloatLogSlider(value=10, base=10, 
                                        min=-10, # max exponent of base
                                        max=10, # min exponent of base
                                        step=0.2, # exponent step
                                        description='$\lambda$ (smooth strength: the larger, the smoother)',
                                        style = {'description_width': 'initial'},
                                        layout=widgets.Layout(width='80%', height='100%'))
        sl_p = widgets.FloatSlider(value=0, min=0, max=1, step=0.1,
                                   description='Asymmetric factor:',
                                   disabled=False, continuous_update=True, orientation='horizontal',readout=True, readout_format='.1f',
                                  style = {'description_width': 'initial'}, layout=widgets.Layout(width='80%', height='100%'))
        sl_niter = widgets.IntSlider(value=20, min=1, max=100, step=1,
                                     description='Number of Iterations:',
                                     disabled=False, continuous_update=True, orientation='horizontal', readout=True, readout_format='d', 
                                     style = {'description_width': 'initial'}, layout=widgets.Layout(width='80%', height='100%'))
        
        #buttons for taking the data
        btn_smooth = widgets.Button(description='record smoothed curve', disabled=False, button_style='', tooltip='Click me', layout=widgets.Layout(width='80%', height='80%'))
        btn_baseline = widgets.Button(description='record baseline', disabled=False, button_style='', tooltip='Click me', layout=widgets.Layout(width='80%', height='80%'))
        
        # interactive controls and displays
        controls = widgets.interactive(self.als, lam = sl_lam, p =sl_p, niter=sl_niter);
        output = controls.children[-1]

        grid =  widgets.GridspecLayout(3, 5, width=str(self.fig[0]*0.65)+'in')
        grid[0, :4] = sl_lam
        grid[1, :4] = sl_p
        grid[2, :4] = sl_niter
        grid[0, 4] = btn_smooth
        grid[1, 4] = btn_baseline
        display(grid)
        display(widgets.VBox([output]))
 
        def on_btn_clicked_smooth(b):
            with output:
                self.data['sm'] = self.data['als']-self.data['bl']
                self.sm_para = [sl_lam.value, sl_p.value, sl_niter.value]
                print("Smoothed curve saved in .data['sm'] (lambda = " + str(sl_lam.value) + ", p = " + str(sl_p.value) + ", n = " + str(sl_niter.value) + ")")
        def on_btn_clicked_baseline(b):
            with output:
                self.data['bl'] = self.data['als']
                self.bl_para = [sl_lam.value, sl_p.value, sl_niter.value]
                print("Baseline saved in .data['bl'] (lambda = " + str(sl_lam.value) + ", p = " + str(sl_p.value) + ", n = " + str(sl_niter.value) + ")")

        btn_smooth.on_click(on_btn_clicked_smooth)
        btn_baseline.on_click(on_btn_clicked_baseline)
    
    def search_peaks(self, height=10, threshold=1, prominence=10, width=1, manu_pk =1, manu_wid = 1):
        """
        height: the height of the peak
        threshold: the difference between the adjacent points around the peak
        prominence: the value between the largest and smallest values
        width: peak width
        """
        if height == self.fp_para[0] and threshold == self.fp_para[0] and prominence == self.fp_para[1]:
            peaks = self.tmpfitpeaks
            para = self.tmpfitpara
            print("no peaks")
        else:
            peaks, para = find_peaks(self.data['sm'], height=height, threshold=threshold, prominence=prominence, width =width)
        num_peaks = len(peaks)
        fig_w = self.fig[0]
        fig_h = 0.3*self.fig[0]+(num_peaks+1)*0.5
        fig_f = 0.3*self.fig[0]
        fig_l = (num_peaks+1)*0.5
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(fig_w,fig_h), gridspec_kw={'height_ratios': [fig_f, fig_l]})
        font_size=14
        ax1.plot(self.data['x'], self.data['sm'])
        # set x, y limits
        xlim = [min(self.data['x']), max(self.data['x'])]
        ax1.set_xlim(xlim)
        min_sm = min(self.data['sm'])
        max_sm = max(self.data['sm'])
        ylim = [min_sm, max_sm]
        ax1.set_ylim(ylim)
        # Draw the height criterion
        ax1.hlines(y=height, xmin = xlim[0], xmax = xlim[1], linewidth=1, color='r')
        # Draw the threshold criterion
        yt1 = np.ones(len(self.data['x']))*(height-threshold)
        yt2 = np.ones(len(self.data['x']))*(height+threshold)
        ax1.fill_between(self.data['x'], yt1, yt2, where=(yt1 < yt2), color='C0', alpha=0.2)
        # Draw the prominence criterion
        yp1 = np.ones(len(self.data['x']))*height
        yp2 = np.ones(len(self.data['x']))*(height-prominence)
        ax1.fill_between(self.data['x'], yp1, yp2, where=(yp1 > yp2), color='C1', alpha=0.2)

        if num_peaks > 0:
            peaks_found = [pd.DataFrame({'code':[int(np.where(peaks==p)[0][0])],
                                            'label': ['tbc'], 
                                            'cen':[round(self.data['x'][p],2)], 
                                            'wid':[round(para['widths'][np.where(peaks==p)][0],2)],
                                            'amp':[round(para['peak_heights'][np.where(peaks==p)][0],2)]}) for p in peaks]
            self.tmp_peaks = pd.concat(peaks_found)
            #display(HTML(self.peaks.to_html()))  
            
            all_peaks = pd.concat([self.tmp_peaks, self.manu_peaks]).reset_index(drop=True)
            all_peaks['code'] = np.arange(len(all_peaks))
            self.add_vlines(ax1, ax1.get_xlim(), all_peaks)
            bbox=[0, 0, 1, 1]
            ax2.axis('off')
            table = ax2.table(cellText = all_peaks.values, bbox=bbox, colLabels=all_peaks.columns, rowLoc='center') #rowLabels=self.tmp_peaks.index,
            #w, h = table[0,1].get_width(), table[0,1].get_height()
            #table.add_cell(0, -1, w,h, text="peak index")
            table.auto_set_font_size(False)
            table.set_fontsize(font_size)
        else:
            print("No peak found!")
        
        # Draw the lines for manually placing the peaks
        
        ax1.vlines(x=manu_pk, ymin = ylim[0], ymax = ylim[1], linewidth=1, color='blue')
        ax1.axvspan(manu_pk-manu_wid/2, manu_pk+manu_wid/2, alpha=0.2, color='blue')
        self.fp_para = [height, threshold, prominence]
        self.tmpfitpeaks = peaks
        self.tmpfitpara = para
    
    def find_peaks(self):
        lb_para = widgets.HTML(value="<b>Parameters for peak sesearching algorithm:</b>")
        
        dy = np.diff(self.data['sm'])
        m_dy = min(abs(dy)) # minimum y incrementals
        sl_h = widgets.FloatSlider(value=round(min(self.data['sm']), 2), min=round(min(self.data['sm']), 2), max=round(max(self.data['sm']),2), step=m_dy, 
                                   description='peak height:',
                                   disabled=False, continuous_update=True, orientation='horizontal',readout=True, readout_format='.1f',
                                   style = {'description_width': 'initial'},
                                   layout=widgets.Layout(width='80%', height='100%'))
        dy=np.diff(abs(self.data['sm']))
        sl_t = widgets.FloatSlider(value=0, min=min(abs(dy)), max=max(abs(dy))/100, step=m_dy,
                                   description='threshold (difference between adjacent points at peak):',
                                   disabled=False, continuous_update=True, orientation='horizontal',readout=True, readout_format='.1f',
                                   style = {'description_width': 'initial'}, layout=widgets.Layout(width='80%', height='100%'))
        sl_p = widgets.FloatSlider(value=0, min=1, max=max(self.data['sm'])-min(self.data['sm']), step=m_dy,
                                   description='prominence (difference between peak and lowset countour):',
                                   disabled=False, continuous_update=True, orientation='horizontal',readout=True, readout_format='.1f',
                                   style = {'description_width': 'initial'}, layout=widgets.Layout(width='80%', height='100%'))
        lb_manu = widgets.HTML(value="<b>Manually adding peaks:</b>")
        
        dx = np.diff(self.data['x'])
        m_dx = min(abs(dx)) # minium x incrementals
        sl_mpk = widgets.FloatSlider(value=min(self.data['x']), min=min(self.data['x']), max=max(self.data['x']), step=m_dx,
                                   description='x position:',
                                   disabled=False, continuous_update=True, orientation='horizontal',readout=True, readout_format='.1f',
                                   style = {'description_width': 'initial'}, layout=widgets.Layout(width='80%', height='100%'))
        sl_mpkw = widgets.FloatSlider(value=m_dx, min=m_dx, max=100*m_dx, step=m_dx,
                                   description='peak width:',
                                   disabled=False, continuous_update=True, orientation='horizontal',readout=True, readout_format='.1f',
                                   style = {'description_width': 'initial'}, layout=widgets.Layout(width='80%', height='100%'))
        

        #buttons for taking the data
        btn_peaks = widgets.Button(description='record peaks', disabled=False, button_style='', tooltip='Click me', layout=widgets.Layout(width='80%', height='80%'))
        btn_addpeaks = widgets.Button(description='add peaks', disabled=False, button_style='', tooltip='Click me', layout=widgets.Layout(width='80%', height='80%'))
        
        # interactive controls and displays
        controls = widgets.interactive(self.search_peaks, height = sl_h, threshold=sl_t, prominence = sl_p, manu_pk =sl_mpk, manu_wid = sl_mpkw);
        output = controls.children[-1]

        grid =  widgets.GridspecLayout(6, 5, width=str(self.fig[0]*0.65)+'in')
        grid[0, :4] = lb_para
        grid[1, :4] = sl_h
        grid[2, :4] = sl_t
        grid[3, :4] = sl_p
        grid[4, :4] = lb_manu
        grid[5, :2] = sl_mpk
        grid[5, 2:4]=sl_mpkw
        
        grid[1, 4] = btn_peaks
        grid[5, 4] = btn_addpeaks
        display(grid)
        display(widgets.VBox([output]))

        def on_btn_clicked_peaks(b):
            with output:
                self.peaks = pd.concat([self.tmp_peaks, self.manu_peaks]).reset_index(drop=True)
                self.peaks['code'] = np.arange(len(self.peaks))
                self.fp_para = [sl_h.value, sl_t.value, sl_p.value]
                print("We have found "+str(len(self.peaks))+ " peaks with the criteria: height = " + str(sl_h.value) + ", threshold = " + str(sl_t.value) + ", prominence = " + str(sl_p.value) + ". We have saved them in .peaks field.")
        
        def on_btn_clicked_addpeaks(b):
            with output:
                newpeak = pd.DataFrame({'code':int(len(self.tmp_peaks.index)+len(self.manu_peaks)),
                                        'label': 'tbc', 
                                        'cen':round(sl_mpk.value,2), 
                                        'wid':round(sl_mpkw.value,2),
                                        'amp':round(max(self.data['y'][(self.data['x']>sl_mpk.value-sl_mpkw.value/2) & (self.data['x']<sl_mpk.value+sl_mpkw.value/2)]), 2)},
                                       index=[int(len(self.tmp_peaks.index))+int(len(self.manu_peaks))])
                self.manu_peaks = pd.concat([newpeak,self.manu_peaks]).reset_index(drop=True)
                clear_output(wait=True)
                print("We have added a new peak.")
                display(newpeak)
                
        btn_peaks.on_click(on_btn_clicked_peaks)
        btn_addpeaks.on_click(on_btn_clicked_addpeaks)
        
    def plot_peaks(self, ax=None, peaks = None, xrange=None):
        peaks = self.peaks if peaks is None else peaks
        if len(peaks.index) >0:
            xr =[min(peaks['cen'])-max(peaks['wid']), max(peaks['cen'])+max(peaks['wid'])] if xrange is None else xrange
            ax1 = self.plot(ax, xrange=xr, title = 'Peaks')
            xydata.add_vlines(ax1, xr, peaks)
            return ax1
        else:
            print("No peak has been identified.")
    
        
    # Fit data using lorentz
    def fit_lorentz(self, peak):
        """
        peak is a dictionary: {"label": 'peak nanme', "cen": center, "wid": width, "amp": amp}, defining initial values
        """
        # Define Lorentz function
        def lorentz(x, y0, amp, cen, wid):
            return y0 + (2*amp/np.pi)*(wid/(4*(x-cen)**2 + wid**2))
        
        # Extract data from the raw data using the range pre-defined in the "peak" parameter (dictionary variable)
        # peak = {'label': '$E_{2g}^1$', 'cen': 379, 'wid': 6, 'amp': 5800}
        dfit = self.data[(self.data['x']>peak['cen']-peak['wid']) & (self.data['x']<peak['cen']+peak['wid'])]
        
        # Remove the background - linear fit using the head and tail of the data
        dht = dfit.iloc[[0,-1]]
        dht = dht.to_numpy()
        dy = dfit['y'] - (dfit['x'] - dht[0,0])*(dht[1,1]-dht[0,1])/(dht[1,0]-dht[0,0])
        
        # Fit the curve
        try:
            popt, pcov = curve_fit(lorentz, dfit.x, dy, p0=[min(dy), (max(dy)-min(dy))*2, peak['cen'], peak['wid']])
            # Calculate the fitted values
            y0, amp, cen, wid = popt
            x_model = np.linspace(min(dfit.x), max(dfit.x), 1000)
            y_model = lorentz(x_model, y0, amp, cen, wid) + (x_model - dht[0,0])*(dht[1,1]-dht[0,1])/(dht[1,0]-dht[0,0])
            amp = y0+2*amp/np.pi/wid + (cen - dht[0,0])*(dht[1,1]-dht[0,1])/(dht[1,0]-dht[0,0])
            cen_dif = cen - peak['cen']
            if type(self).__name__ == 'raman' :
                shift_type = "blue" if cen_dif > 0 else "red"
                #display(Latex(f"The experimental peak shows a " + shift_type + " shift of " + str(round(cen_dif,2)) + " cm$^{-1}$."))

            return {'label':peak['label'], 'cen': cen, 'wid': abs(wid), 'amp': amp,'xfit': x_model, 'yfit': y_model, 'pcov': pcov};
        except:
            print('The fitting fails. Refine the peak and try again.')
            return peak.update({'xfit': dfit['x'], 'yfit': dfit['y'], 'pcov': None})        
    
    # plot fitting
    def plot_fitting(self, peak, aspect = 0.4):
        """
        peak is the output of fit_lorentz function
        {"label", "cen", "amp", "xfit", "yfit", "pcov"}
        """
        xmin = peak['cen']-peak['wid']
        xmax = peak['cen']+peak['wid']
        ref = self.refpeaks[(self.refpeaks['cen']>xmin) & (self.refpeaks['cen']<xmax)]
        num_refs = len(ref.index)
        fig_w = self.fig[0]
        fig_h = 0.3*self.fig[0]+(num_refs+1)*0.5
        fig_f = 0.15*self.fig[0]
        fig_l = (num_refs+1)*0.5
        
        fig, (ax0, ax1, ax2) = plt.subplots(3, 1, figsize=(fig_w,fig_h), gridspec_kw={'height_ratios': [fig_f, fig_f, fig_l]}, constrained_layout=True)
        #plt.tight_layout()
        
        # plot the full range and add a vertical line in the full range data for the peak
        self.plot_peaks(ax=ax0, xrange=[min(self.data['x']), max(self.data['x'])])
        ylim = ax0.get_ylim()
        ax0.vlines(x=peak['cen'], ymin = ylim[0], ymax = ylim[1], color='red')
        
        # Plot the fitting with raw data and reference line
        ax1.set_facecolor(self.fig[1])
        ax1.set_xlabel(self.xlabel, fontsize = 16)
        ax1.set_ylabel(self.ylabel, fontsize = 16)          
        
        dfit = self.data[(self.data['x']>xmin) & (self.data['x']<xmax)] # select raw data
        ax1.scatter(dfit.x, dfit.y) # raw data
        ax1.errorbar(dfit.x, dfit.y, dfit.err, ls='', color = 'k') # errors
        ax1.plot(peak['xfit'], peak['yfit'], color='r') # fitting

        ymin, ymax = ax1.get_ylim()
        ymax = ymax+0.1*(ymax-ymin)
        ax1.axvline(peak['cen'], ymin=0, ymax = (peak['amp']-ymin)/(ymax-ymin), color='grey', linestyle='--')
        ax1.set_ylim(ymin, ymax)
        ax1.annotate(peak['label']+": "+"{:.2f}".format(peak['cen']), xy=(peak['cen'], peak['amp']), xycoords='data', size=16, ha='center', va='bottom', color = 'blue')
        
        # Evaluate the errors in fitting
        rect = [0.8,0,0.2,1]
        ax1.set_xlim([xmin, xmax + 0.25*(xmax-xmin)])
        ax1_inset = ax1.inset_axes([0.85,0,0.2,1])
        ax1_inset.axis('off')
        im2 = ax1_inset.imshow(np.log(np.abs(peak['pcov'])))
        #fig.colorbar(im2, ax = ax1_inset)

        # Add reference peaks in the range of the selected peak
        if num_refs >0:
            ref_draw = ref.drop(['label'], axis=1)
            ref_draw.insert(loc=0, column = 'label', value=[str(i) for i in np.arange(len(ref))])
            ref.insert(loc=0, column = 'index', value= [str(i) for i in np.arange(len(ref))])
            xydata.add_vlines(ax1, [xmin, xmax], ref_draw, frompeak=False, linecolor ='blue') # add the reference line
            bbox=[0, 0, 1, 1]
            font_size = 14
            ax2.axis('off')
            ax2.set_title('Reference peaks from literature', loc ='left')
            table = ax2.table(cellText = ref.values, bbox=bbox, colLabels=ref.columns, rowLoc='center') #rowLabels=self.tmp_peaks.index,
            table.auto_set_font_size(False)
            table.set_fontsize(font_size)
        else:
            ax2.axis('off')
        plt.show()
    
    # analyze identified peaks
    def analyse_peaks(self, peak_selected):
        if len(self.peaks.index) == 0:
            print("No peak has been identified.")
            return False
        
        def unpack_options(peak):
            code, label, cen = peak.split(' ')
            cen = float(cen)
            code = int(code)
            return code, label, cen
        
        # Select the peak 
        code, label, cen = unpack_options(peak_selected)
        peak = self.peaks[self.peaks['code']==code]
        
        if len(peak.index)>0:
            self.tmp_peakfit = self.fit_lorentz(peak.iloc[0].to_dict())
            if self.tmp_peakfit is None:
                print('peak fitting failed.')
            else:
                self.plot_fitting(self.tmp_peakfit)
        else:
            print('No peak selected.')
        
    
    # process peaks with widgets
    def process_peaks(self):
        if len(self.peaks.index) == 0:
            print("No peak has been identified.")
            return False
        
        # Format the labels for the peaks
        def pack_options(peaks):
            try:
                peaks = peaks.reset_index(drop=True)  # make sure indexes pair with number of rows
                peaks['code'] = np.arange(len(peaks))
            except:
                print('I cannot pack options for the widgets.')
                return False
            options = []
            labels = []
            for index, row in peaks.iterrows():
                options.append('{} {} {}'.format(row['code'],row['label'],row['cen']))
                labels.append(row['label'])
            return options, labels
        
        # Peaks found from the raw data
        options, labels = pack_options(self.peaks)
        lb_peaks = widgets.HTML(value="<b>Choose a peak:</b>")
        dp_peaks = widgets.Dropdown(placeholder='choose a peak',options=options, value=options[0],
                                    description='select a peak:',
                                    disabled=False, continuous_update=True, orientation='horizontal',readout=True, readout_format='.1f',
                                    style = {'description_width': 'initial'}, layout=widgets.Layout(width='80%', height='80%'))
        txt_label = widgets.Text(value=labels[0], placeholder='enter a label for the peak', description='peak label:',
                                 disabled=False, continuous_update=True, orientation='horizontal',readout=True, readout_format='.1f',
                                 style = {'description_width': 'initial'}, layout=widgets.Layout(width='80%', height='80%'))
        
        # buttons for taking the data
        btn_delete_peak = widgets.Button(description='delete peak', disabled=False, button_style='', tooltip='Click me', layout=widgets.Layout(width='80%', height='80%'))
        btn_update_peak = widgets.Button(description='update peak', disabled=False, button_style='', tooltip='Click me', layout=widgets.Layout(width='80%', height='80%'))

        controls = widgets.interactive(self.analyse_peaks, peak_selected=dp_peaks);
        output = controls.children[-1]

        # Button controls
        def on_btn_delete_peak(b):
            if len(self.peaks.index) == 1:
                print("Only 1 peak left. You cannot delete it.")
                return
            with output:
                code, label, cen = dp_peaks.value.split(' ')
                self.peaks = self.peaks[self.peaks['code'] != int(code)]
                print("peak "+dp_peaks.value+ " has been deleted.")
                clear_output(wait=True)
                try:
                    self.peaks = self.peaks.reset_index(drop=True)  # make sure indexes pair with number of rows
                    self.peaks['code'] = np.arange(len(self.peaks))
                except:
                    pass
                options, labels = pack_options(self.peaks)
                dp_peaks.options = options

        btn_delete_peak.on_click(on_btn_delete_peak)

        def on_btn_update_peak(b):
            if len(self.peaks.index) == 0:
                print("No peak has been identified.")
                return False
            with output:
                code, label, c = dp_peaks.value.split(' ')
                self.peaks.loc[self.peaks['code']==int(code),'label']=txt_label.value
                self.peaks.loc[self.peaks['code']==int(code),'cen']=round(self.tmp_peakfit['cen'],2)
                self.peaks.loc[self.peaks['code']==int(code),'amp']=round(self.tmp_peakfit['amp'],2)
                self.peaks.loc[self.peaks['code']==int(code),'wid']=round(self.tmp_peakfit['wid'],2)
                #self.peaks.loc[int(i), 'xfit']=self.tmp_peakfit['xfit']
                #self.peaks.loc[int(i), 'yfit']=self.tmp_peakfit['yfit']
                #self.peaks.loc[int(i), 'pcov']=self.tmp_peakfit['pcov']
                print("peak "+dp_peaks.value+ " has been updated.")
                options, labels = pack_options(self.peaks)
                dp_peaks.options = options

        btn_update_peak.on_click(on_btn_update_peak)
        
        # Plot the controls
        grid =  widgets.GridspecLayout(2, 6, width=str(self.fig[0]*0.65)+'in')
        grid[0, :] = lb_peaks
        grid[1, :2] = dp_peaks
        grid[1, 2:4] = txt_label
        grid[1, 4] = btn_update_peak
        grid[1, 5] = btn_delete_peak
        
        display(grid)
        display(widgets.VBox([output]))

        # display(HTML(refpeak.to_html())) 
        
    #Correct curve with the reference peak
    def correct_x(self, refpeak, fitted):
        """
        refpeak: the reference peak, dictionary
        fitted: the fitted peak from self.fit_lorentz(refpeak)
        """
        dif = refpeak['cen'] - fitted['cen']
        self.data['x'] = self.data['x'] + dif
        self.peaks['cen'] = self.peaks['cen'] + dif
 
    
    # plot the raw data
    def plot(self, ax=None, xrange=None, title=None, aspect=0.2):
        if ax is None:
            plt.clf()
            fig, ax = plt.subplots(1, 1, figsize=(self.fig[0],aspect*self.fig[0]))
        
        if xrange is None:
            xmin = min(self.data.x)
            xmax = max(self.data.x)
        else:
            xmin = xrange[0]
            xmax = xrange[1]
        d = self.data[(self.data['x']>xmin)&(self.data['x']<xmax)]
        
        ax.set_facecolor(self.fig[1])
        ax.plot(d.x, d.y, 'o--', ms = 3, color = 'black', linewidth=1, label = self.legend)
       
        #ax.set_yticklabels('')
        ymin, ymax = ax.get_ylim()
        ymax = ymax+0.1*(ymax-ymin)
        ax.set_ylim([ymin, ymax])
        ax.set_xlim(xrange)
        
        ax.set_xlabel(self.xlabel, fontsize = 16)
        ax.set_ylabel(self.ylabel, fontsize = 16)
        ax.legend()
        ax.title.set_text(self.title if title==None else title)
        
        return ax
    
    # Draw a curve and/or mark peak seperation peak[0], peak position; peak[1] FWHM
    def peak_seperation(self, peak1, peak2, ax=None, title = None, ext=1.5, aspect=0.2):
        if ax is None:
            plt.clf()
            fig, ax = plt.subplots(1, 1, figsize=(self.fig[0],aspect*self.fig[0]))
            
        xmin = min(peak1['cen']-ext*peak1['wid'], peak2['cen']-ext*peak2['wid'])
        xmax = max(peak1['cen']+ext*peak1['wid'], peak2['cen']+ext*peak2['wid'])
        
        
    
        d = self.data[(self.data['x']>xmin)&(self.data['x']<xmax)]
        ymin = min(d.y)
        ht = ymin+ (min(peak1['amp'], peak2['amp'])-ymin)/2
        ax.set_facecolor(self.fig[1])
        ax.annotate(text =' ',xy=(min(peak1['cen'], peak2['cen']), ht), xycoords='data',
                    xytext=(max(peak1['cen'], peak2['cen']), ht),textcoords='data',
                    arrowprops=dict(arrowstyle="<->"),va='center')
        ax.annotate(text="$\Delta\omega=$"+"{:.1f} ".format(abs(peak2['cen'] - peak1['cen'])) + self.quantity[1],
                    xy=(((peak1['cen']+peak2['cen'])/2), ht), 
                    xycoords='data',fontsize=16.0,textcoords='data',ha='center', va='center',  
                    bbox=dict(facecolor=self.fig[1], alpha=1, edgecolor=self.fig[1]))
        ax.title.set_text(self.title if title == None else title)
        self.plot(ax, [xmin, xmax])
        
        # Add vertical lines
        peaks = pd.concat([pd.DataFrame({'label':[p['label']], 'cen': [p['cen']], 'amp': [p['amp']]}) for p in [peak1, peak2]], ignore_index=True)
        xydata.add_vlines(ax, [xmin, xmax], peaks)
    
    @staticmethod
    def add_vlines(ax, xrange, peaks, frompeak=True, linecolor='grey'):
        [ymin, ymax] = ax.get_ylim()
        
        vlines = peaks #
        vl = vlines[(vlines['cen']>xrange[0])&(vlines['cen']<xrange[1])]
        
        try:
            vl = vl.reset_index(drop=True)
        except:
            pass
        for index, row in vl.iterrows():
            vp = (row['amp']-ymin)/(ymax-ymin) if frompeak is True else 1
            ax.axvline(row['cen'], ymin = 0, ymax = vp, color=linecolor, linestyle='--') 
            ax.annotate('$'+row['label']+'$', xy=(row['cen'], row['amp'] if frompeak is True else ymax), xycoords='data', size=16, ha='center', va='bottom', color = 'black')
    
    @staticmethod
    def multiple_xy_stack (data, xrange = None, title=None, vlines = None, shiftfactor = 1.01, aspect=0.2, legendloc = 'upper right'):
        if all(type(element) == type(data[0]) for element in data) == False:
            print('The data do not have the same type and they cannot be stacked.')
            return False
        plt.clf()
        plt.rcParams['font.size'] = '16'
        
        fig, ax = plt.subplots(1, 1, figsize = (data[0].fig[0],aspect*data[0].fig[0]))
        
        colors = sns.color_palette("rocket", len(data))
        vshift = 0
        i = 0
        for s in data:
            if xrange !=None:
                d = s.data[(s.data['x']>xrange[0])&(s.data['x']<xrange[1])]
            else:
                d = s.data
                xrange = [min(s.data.x), max(s.data.x)]
            ax.plot(d.x, d.y - vshift, 'o--', color =colors[i], ms=4, mfc=colors[i], label = s.legend)
            vshift = vshift + (max(d.y)-min(d.y))*shiftfactor
            i += 1
        
        if xrange is not None:
            ax.set_xlim(xrange)
            
        ymin, ymax = ax.get_ylim()
        ymax = ymax + (ymax-ymin)*len(data)*0.01
        if vlines is not None:
            vlines['y'] = ymax*np.ones(len(vlines))
            xydata.add_vlines(ax, xrange, vlines) 
        ax.set_facecolor(data[0].fig[1])
        ax.set_ylim(ymin, ymax)
        ax.set_yticklabels('')
        ax.set_xlabel(data[0].xlabel, fontsize = 16)
        ax.set_ylabel(data[0].ylabel, fontsize = 16)
        ax.title.set_text(data[0].title if title is None else title)
        
        plt.legend(loc=legendloc, fancybox=True, framealpha=0.5)  #ncol= len(Spectra)
        
