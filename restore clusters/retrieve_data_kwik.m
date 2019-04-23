function [spiketimes, clusternumbers, spikesamples, ...
	flt, clusters, groups, group_names] = retrieve_data_kwik(filename,clusters_source)

if nargin<2
	clusters_source = 'main';
end
% Extracts information from a kwik file
% filename = path of the file
% clusters_source = 'main' to retrieve the actual state or 'original' to
% retrieve the automatic clustering

%% read spikes info
spikesamples = hdf5read(filename, '/channel_groups/0/spikes/time_samples');
clusternumbers = double(hdf5read(filename, ['/channel_groups/','0','/spikes/clusters/',clusters_source]));
flt.path = char(fileparts(filename));
flt.datfilename = char(h5readatt(filename, '/application_data/spikedetekt/','raw_data_files'));
flt.n_channels = double(h5readatt(filename, '/application_data/spikedetekt/','n_channels'));
flt.sample_rate = h5readatt(filename, '/application_data/spikedetekt/','sample_rate');
flt.filter_high_factor = h5readatt(filename, '/application_data/spikedetekt/','filter_high_factor');
flt.filter_low = h5readatt(filename, '/application_data/spikedetekt/','filter_low');
flt.filter_high = flt.sample_rate/2 * flt.filter_high_factor;
flt.filter_butter_order = h5readatt(filename, '/application_data/spikedetekt/','filter_butter_order');

spiketimes = double(spikesamples) / flt.sample_rate;

%% read info related to waveforms
% extract_s_after = hdf5read(filename, '/application_data/spikedetekt/','extract_s_after');
% extract_s_before = hdf5read(filename, '/application_data/spikedetekt/','extract_s_before');
%
% raw_data_files = hdf5read(filename, '/application_data/spikedetekt/','raw_data_files');
% datfile = raw_data_files.Data;
%
% nchannels = double(h5readatt(filename,'/application_data/spikedetekt','n_channels'));

%% read group for each channel
clusters = unique(clusternumbers);
groups = zeros(length(clusters),1);

for i = 1:length(clusters)
	ci = clusters(i);
	% add 1 because it starts from 0
	groups(i) = h5readatt(filename,...
		['/channel_groups/0/clusters/' clusters_source '/' num2str(ci)],'cluster_group') ...
		+ 1;
end

%% read group names
ngroups = h5info(filename,['/channel_groups/0/cluster_groups/' clusters_source]);
ngroups = length(ngroups.Groups);
group_names = cell(ngroups,1);
for i = 1:ngroups
	group_names{i} = h5readatt(filename,['/channel_groups/0/cluster_groups/' clusters_source '/' num2str(i-1)],'name');
end
