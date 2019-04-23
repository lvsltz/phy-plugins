# tested on phy development version May 22 2017

from phy import IPlugin
import numpy as np
import matplotlib.pyplot as plt

class FiringRateView(IPlugin):
    def attach_to_controller(self, c):

        # Create the figure when initializing the GUI.
        f, ax = plt.subplots()
        r = f.patch
        r.set_facecolor('black')
        ax.set_axis_bgcolor((0, 0, 0))
        #c.n_spikes_waveforms = 150
        @c.connect
        
        def on_gui_ready(gui):
            # Called when the GUI is created.

            # We add the matplotlib figure to the GUI.
            gui.add_view(f, name='Firing rate')
            mycolors = ['#0892FC','#FF0202','#F0FD02','#E41FE4','#02D902','#FF9302','#D49646','#CD83C9','#C9AC24','#96B33E'] 
                    
            # We connect this function to the "select" event triggered
            # by the GUI at every cluster selection change.
            @gui.connect_
            def on_select(clusters,**kwargs):
                # We clear the figure.
                if not clusters:
                    return
                ax.clear()
                # We compute the ISI for all selected clusters
                nbins = 350
                duration = c.model.duration
                bins = np.linspace(0, duration, nbins)
                spikesall = np.sort(np.concatenate([c._get_spike_times(cluster,True).data for cluster in clusters]),axis=None)
                for ci in range(0,len(clusters)):
                    cluster = clusters[ci]
                    spikes = c._get_spike_times(cluster,True).data
                    y_cluster, bin_edges = np.histogram(spikes,bins=bins)
                    fr = y_cluster/(duration/nbins)
                    ax.plot(fr,'-',color=mycolors[min(ci,len(mycolors)-1)])
                
                # plot combined
                if len(clusters)>1:
                    y_all, bin_edges = np.histogram(spikesall,bins=bins)
                    fr_all = y_all/(duration/nbins)
                    ax.plot(fr_all,'-',color='white',alpha = 0.5)
                
                ax.xaxis.label.set_color('white')
                ax.yaxis.label.set_color('white')
                ax.tick_params(axis='x', colors='white')
                ax.tick_params(axis='y', colors='white')
                ax.yaxis.set_ticks_position('left') 
                ax.axes.get_xaxis().set_visible(False)
                f.tight_layout()
                
                # We update the figure.
                f.canvas.draw()

