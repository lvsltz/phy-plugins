# tested on phy development version May 22 2017

import numpy as np
from phy import IPlugin


class ColumnISI(IPlugin):
    def attach_to_controller(self, controller):
        refractory = 2
        ctx = controller.context
        @controller.supervisor.connect
        def on_create_cluster_views():
            @controller.supervisor.add_column(name='isi_'+str(refractory))
            @ctx.memcache
            def calculate_isi(cluster_id):
                data = 0
                bw = 0.001 # bin width in seconds
                nbins = refractory
                xlim = (nbins+1)/1000
                spikes = controller._get_spike_times(cluster_id,True).data
                bins = np.arange(0, xlim, bw)
                y,bin_edges = np.histogram(np.diff(spikes),bins=bins)
                y = y/(len(spikes)-1)*100 #percents
                data = sum(y[range(refractory)])
                return data

