function klusta_restore_original_clusters(filepath, ClusterToSplit, boolWrite)
% This script shows the original clusters ClusterToSplit is made of
% and splits it to restore the original structure in a given kwik file.
%
% It saves a backup file before any change.
%
% filename = .kwik file path
% ClusterToSplit = cluster  number that needs to be restored
% boolWrite = 1 save changes; boolWrite = 0 only shows information
%
% Tested with phy v1.0.9 development version (May 22, 2017).
%
% Example calls:
% klusta_restore_original_clusters
% klusta_restore_original_clusters('abc.kwik')
% klusta_restore_original_clusters('abc.kwik', 123)
% Details at the end.

if nargin<3
	% by default nothing gets changed, only shows info
	boolWrite = 0;
end

showMerges = 0;

% if no input provided look for kwik files in the current folder
if nargin==0
    fnames = dir([pwd filesep '*.kwik']);
    if ~isempty(fnames)
        filepath = fnames(1).name;
    else
        disp('No kwik file found.')
        return
    end
end
filepath = which(filepath); % get full path
[folderkwik,filename,filext] = fileparts(filepath);

% original information
fprintf('\n')
fprintf('Reading original clusters in %s%s ...\n',filename,filext);
[~, orig_spikeclusters, ~, ~, orig_clusters, ~, orig_group_names] = ...
    retrieve_data_kwik(filepath,'original');
orig_spikeclusters_unaltered = orig_spikeclusters;

% main (actual) information
fprintf('Reading present clusters in %s%s ...\n',filename,filext);
[~, main_spikeclusters, ~, ~, main_clusters, main_groups, main_group_names] = ...
    retrieve_data_kwik(filepath,'main');
main_spikeclusters_unaltered = main_spikeclusters;

fprintf('\nNumber of clusters original / now: %u / %u\n',...
    length(orig_clusters),length(main_clusters))
fprintf('Max cluster now: %u\n',max(main_clusters))

L = fliplr(regexprep(fliplr(num2str(length(orig_spikeclusters))),'\d{3}(?=\d)', '$0.'));
fprintf('Number of spikes: %s\n',L) 

disp('Groups')
for ii=1:length(main_group_names)
    fprintf('  %s: %u\n',main_group_names{ii}{1},sum(main_groups==ii))
end


%% shows summary of all clusters

if showMerges
    reclusterings_orig = cell(length(main_clusters),1);
    reclusterings_main = reclusterings_orig;
    
    k = 0;
    for ii = 1:length(main_clusters)
        ci = main_clusters(ii);
        
        % find spikes for cluster ci
        spikes_ci = main_spikeclusters_unaltered == ci;
        
        % find original corresponding clusters after merging/reclustering
        clusters_within = unique(orig_spikeclusters(spikes_ci));
        
        % find if any previous cluster contains the same orig cluster
        % which would indicate reclustering
        overlap = find(cellfun(@(x) sum(ismember(clusters_within,x))>0,reclusterings_orig));
        
        if ~isempty(overlap)
            reclusterings_orig{overlap(1),1} = unique([reclusterings_orig{overlap}; clusters_within]);
            reclusterings_main{overlap(1),1} = unique([reclusterings_main{overlap}; ci]);
        else
            k = k+1;
            reclusterings_orig{k,1} = clusters_within;
            reclusterings_main{k,1} = ci;
        end
    end
        
    fprintf('Merges (main=1)/reclusterings (main>1)\n')
    fprintf('main: orig\n')
    
    reclusterings_orig = reclusterings_orig(1:k);
    reclusterings_main = reclusterings_main(1:k);
    % printing
    for ii = 1:length(reclusterings_orig)
        if length(reclusterings_main{ii})> 1 || length(reclusterings_orig{ii})>1
            main = strip(sprintf('%u ',reclusterings_main{ii}));
            fprintf('\n%s:\n',main)
%             fprintf('- ')
            
            orig = strip(sprintf('%u %u %u %u %u %u %u %u %u %u\n',reclusterings_orig{ii}));
            fprintf('%s%s',blanks(5),orig)
            fprintf('\n')
        end
    end
    
end
if nargin < 2
    return
end


% select spikes that are wrongly assigned to the cluster to be split
spikes_to_change = main_spikeclusters == ClusterToSplit;
if sum(spikes_to_change)<1
    fprintf('\nCluster doesn''t exist.\n')
    return
end

% split cluster ClusterToSplit to original state
fprintf('\nCluster to split\n   %u (%s)\n',ClusterToSplit,main_group_names{main_groups(main_clusters==ClusterToSplit)}{1})
main_spikeclusters(spikes_to_change) = orig_spikeclusters(spikes_to_change);

clus_to_restore = unique(orig_spikeclusters(spikes_to_change));

% count no of spikes
fprintf('%u clusters to restore (No of spikes now / No of spikes original)\n', length(clus_to_restore))
for i=1:length(clus_to_restore)
	ci = clus_to_restore(i);
	no_spikes_main = numel(find(orig_spikeclusters(spikes_to_change) == ci));
	no_spikes_original = numel(find(orig_spikeclusters == ci));
	fprintf('   %u (%u/%u)\n', clus_to_restore(i), no_spikes_main, no_spikes_original)
	
	if no_spikes_main~=no_spikes_original
		% In case some spikes are in other MAIN clusters, not ClusterToSplit,
		% this lists below the MAIN clusters that contain some
		% of the original spikes. 
		% See the introduction below.
        
		other_clusters = setdiff(unique(main_spikeclusters(orig_spikeclusters == ci)),ci);
		for oi = other_clusters'
			fprintf('     %u (%u)\n',oi, numel(find(main_spikeclusters == oi & orig_spikeclusters==ci)))
		end
	end
end
fprintf('\n')



%% operate changes
if boolWrite && input(sprintf('\nAre you sure? [1/0]\n'))
	% Create backup
	datenow = datestr(datetime('now'), '_yyyy_mm_dd__HH_MM');
	try
		if ~exist(fullfile(folderkwik,'backup'),'dir')
			mkdir(fullfile(folderkwik,'backup'))
            disp('Backup folder created.')
		end
		copyfile(filepath,fullfile(folderkwik,'backup', [filename datenow '.bak']))
		disp('Backup saved.')
	catch
		disp('Backup failed. kwik not modified.')
		return
	end
	
	% Modify kwik file
	try
		h5write(filepath,['/channel_groups/','0','/spikes/clusters/main'],int32(main_spikeclusters))
		
		id_unsorted = find(strcmpi([orig_group_names{:}], 'unsorted')) - 1 ; % python counts from 0
		for ci=clus_to_restore'
			
			h5writeatt(filepath,['/channel_groups/','0','/clusters/main/' num2str(ci)],'cluster_group',id_unsorted)
		end
		disp('Clusters restored.')
	catch
		disp('Process failed. Please restore the backup.')
	end
end




% Example: Let's consider 2 clusters A and B (ORIGINAL).
% They are merged into cluster C (MAIN). A and B will disappear.
% We close phy. 
% We call this function for cluster C. 
% We open phy. A and B appear again and C is gone.
%
% Example input:
% klusta_restore_original_clusters('abc.kwik', 211)
% 
% Example output:
% Cluster to split
%    211
% 2 clusters to restore (No of spikes now / No of spikes original)
%    8 (525/525)
%    61 (831/831)
%
%
% In case some spikes are in other MAIN* clusters, not ClusterToSplit,
% the code lists the MAIN clusters that contain some of the original spikes. 
% This happens because at least one reclustering happened.
% The MAIN clusters in this case won't be affected. If a complete restore is
% desired, one needs to merge the clusters listed here with
% ClusterToSplit, and then call the function on the big cluster.
% Example: Merge MAIN clusters 220 and 221 to restore everything as
% in the original kwik (ORIG*). See the output of showMerges = 1 for
% additional clusters involved.
% 
% Cluster to split
%    221
% 3 clusters to restore (No of spikes now / No of spikes original)
%    21 (1021/1037)
% 	   220 (16)
%    51 (2784/2784)
%    57 (21066/21189)
% 	   220 (123)
%
% * MAIN vs ORIG: main represents the most updated changes after the kwik
% file is saved. ORIG indicates the clusters as obtained from the automatic
% clustering. Both the original (orig) and the original (main) clusterings
% are saved in a kwik file.