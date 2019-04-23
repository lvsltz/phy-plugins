# tested on phy development version May 22 2017
from phy import IPlugin
import numpy as np
import matplotlib.pyplot as plt


class ISIViewTraces(IPlugin):
    def attach_to_controller(self, c):


        # Create the figure when initializing the GUI.
        f, ax = plt.subplots()
        r = f.patch
        r.set_facecolor('black')
        ax.set_axis_bgcolor((0, 0, 0))

        @c.connect
        def on_gui_ready(gui):
            # Called when the GUI is created.

            # We add the matplotlib figure to the GUI.
            gui.add_view(f, name='ISI')
            mycolors = ['#0892FC','#FF0202','#F0FD02','#E41FE4','#02D902','#FF9302','#D49646','#CD83C9','#C9AC24','#96B33E']
            # We connect this function to the "select" event triggered
            # by the GUI at every cluster selection change.
            @gui.connect_
            def on_select(clusters, **kwargs):
                if not clusters:
                    return
                # We clear the figure.
                ax.clear()

                # We compute the ISI.
                bw = 0.001 # bin width in seconds
                nbins = 25
                xlim = (nbins+1)/1000
                refractory = 2 #ms
                firstbins = np.zeros(int((xlim-bw)*1000))

                if len(clusters)==1:
                    nclusters = 1
                else:
                    nclusters = len(clusters)+1 # when more clusters, also plot ISI for combined
                    spikesall = np.sort(np.concatenate([c._get_spike_times(cluster, True).data for cluster in clusters]),axis=None)

                for ci in range(0,nclusters):
                    if ci<len(clusters):
                        cluster = clusters[ci]
                        spikes = c._get_spike_times(cluster, True).data
                        ccolor = mycolors[ci % len(mycolors)]
                        lw = 2.0
                        alpha = 1
                    else:
                        spikes = spikesall
                        ccolor = '#FFFFFF'
                        lw = 2.0
                        alpha = 0.5

                    bins = np.arange(0, xlim, bw)
                    y, bin_edges = np.histogram(np.diff(spikes),bins=bins)
                    if len(spikes)==1:
                        return
                    y = y/(len(spikes)-1)*100 #percents
                    firstbins[ci] = sum(y[range(refractory)])
                    bins = bins*1000
                    ax.plot([bins[0], bins[0]],[0, y[0]],color=ccolor,linewidth=lw,alpha=alpha) # vertical first
                    for li in range(1,len(y)): # vertical
                        ax.plot([bins[li], bins[li]],[y[li-1], y[li]],color=ccolor,linewidth=lw,alpha=alpha)
                    for li in range(0,len(y)): # horizontal
                        ax.plot([bins[li], bins[li+1]],[y[li], y[li]],color=ccolor,linewidth=lw,alpha=alpha)
                    ax.plot([bins[len(y)], bins[len(y)]],[0, y[len(y)-1]],color=ccolor,linewidth=lw,alpha=alpha) # vertical end

                ax.set_xticks(np.concatenate(([0,refractory],np.arange(10,nbins+1,10))))

                ylims = ax.get_ylim()
                ypos = ylims[1]*0.1
                xpos = nbins/2

                rect_alpha = 0.8
                ax.text(xpos,ylims[1]-1*ypos,'Best (%u) %.2f%%' % (clusters[0],firstbins[0]),alpha = 0.7,fontsize = 14,color=mycolors[0],bbox=dict(facecolor='black',alpha=rect_alpha))
                #ax.plot([refractory, refractory],[0, ylims[1]],color='white',linewidth=1,alpha=0.7) # refractory period demarcation

                if len(clusters)>1:
                    ax.text(xpos,ylims[1]-2*ypos,'Similar (%u) %.2f%%' % (clusters[1],firstbins[1]),alpha = 0.7,fontsize = 14,color=mycolors[1],bbox=dict(facecolor='black',alpha=rect_alpha))
                    ax.text(xpos,ylims[1]-3* ypos,'Group %.2f%%' % firstbins[len(clusters)],alpha = 0.7,fontsize = 14,color='white',bbox=dict(facecolor='black',alpha=rect_alpha))

                ax.set_xlim([-bw*1000, xlim*1000])

                ax.xaxis.label.set_color('white')
                ax.yaxis.label.set_color('white')
                ax.tick_params(axis='x', colors='white')
                ax.tick_params(axis='y', colors='white')
                ax.xaxis.set_ticks_position('bottom')
                ax.yaxis.set_ticks_position('left')
                f.tight_layout()

                # We update the figure.
                f.canvas.draw()
