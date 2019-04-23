# tested on phy development version May 22 2017

# This function calculates the minimal channel distance between "best cluster"
# and all remaining "similar clusters" (before and after current channel)
# It assumes the probe is liniar.
# If more than a given number of channels have been checked, it turns green
# to indicate further checking is useless because neurons are too far apart.
# 
# This plugin also visually indicates which conda environment is used.
# This is useful if multiple instances are run simultaneously.

from phy import IPlugin
import numpy as np
import matplotlib.pyplot as plt
import os


class BasicInfo(IPlugin):
    def attach_to_controller(self, c):


        # Create the figure when initializing the GUI.
        f, ax = plt.subplots()
        ax.axis('off')
        r = f.patch
        mycolors = ['#0892FC','#FF0202','#F0FD02','#E41FE4','#02D902','#FF9302','#D49646','#CD83C9','#C9AC24','#96B33E']
        if os.environ['CONDA_DEFAULT_ENV']=='phy':
            colno = 0 
        else:
            colno = 1
        bkndcolors = ['#000000','#707070']
        r.set_facecolor(bkndcolors[colno])
        ax.set_axis_bgcolor(bkndcolors[colno])
        @c.connect
        def on_gui_ready(gui):
            # Called when the GUI is created.

            # We add the matplotlib figure to the GUI.
            gui.add_view(f, name='Basic info')
            # We connect this function to the "select" event triggered
            # by the GUI at every cluster selection change.
            @gui.connect_
            def on_select(clusters, **kwargs):
                if not clusters:
                    return
                # We clear the figure.
                ax.clear()

                sim = c.similarity(clusters[0])
                best_sim_ch = np.zeros(len(sim))
                current = -1
                if len(clusters)>1:
                    for index in range(0,len(sim)):
                        if sim[index][0]==clusters[1]:
                            current = index
                        best_sim_ch[index] = c.get_best_channel(sim[index][0])
                    ch_clus_0 = c.get_best_channel(clusters[0])
                    # ch_clus_1 = c.get_best_channel(clusters[1])
                    # current_dist = abs(ch_clus_1-ch_clus_0)
                    youcanstop = 0
                    closest_dists = best_sim_ch[current:] - ch_clus_0
                    closest_dist = np.amin(abs(best_sim_ch[current:] - ch_clus_0))

                    closest_dist_neg = -1 # before current channel
                    closest_dist_pos = -1 # after current channel

                    try:
                        closest_dist_neg = np.amin(abs(closest_dists[np.where(closest_dists<=0)]))
                    except ValueError:
                        pass

                    try:
                        closest_dist_pos = np.amin(abs(closest_dists[np.where(closest_dists>=0)]))
                    except ValueError:
                        pass
                    # turns green if at least x=3 channels around there is no other similar cluster
                    youcanstop = closest_dist>3

                # signal if checking similar clusters can stop
                # and shows min distance before and after current channel
                xlims = ax.get_xlim()
                ylims = ax.get_ylim()
                xpos = xlims[1]/2
                ypos = ylims[1]*0.9


                if len(clusters)>1:
                    col = mycolors[1]
                    if youcanstop:
                        col = mycolors[4]
                    ax.text(xpos,ypos,'%d %d'%(closest_dist_neg,closest_dist_pos),ha='center',alpha = 0.7,fontsize = 14,color='white',bbox=dict(facecolor=col,alpha=0.8))

                #ax.axes.get_xaxis().set_visible(False)
                #ax.axes.get_yaxis().set_visible(False)
                ax.axis('off')
                #f.tight_layout()

                # We update the figure.
                f.canvas.draw()
