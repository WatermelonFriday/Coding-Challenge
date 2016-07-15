import sys
import networkx as nx
import time
from calendar import timegm
from numpy import median
from json import loads


def main():
    if len(sys.argv) != 3:
        raise ValueError('Need both input and output paths (and only that).')
    
    # initialize graph
    G = nx.Graph()
    
    # initialize time objects
    timestamp_upper = time.time() # this should be disabled (below) if streaming data are used
    timestamp_lower = timegm(time.strptime('2009-04-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ'))
    maxtimestamp = timestamp_lower
    
    # initialize median_degree until first median_degree found
    median_degree = None
    
    # open output file
    with open(sys.argv[2], 'w') as results:
    
        # open input file using universal newlines
        with open(sys.argv[1], 'rU') as f:
            for fline in f:
                
                # process non-empty lines only
                if fline.strip():
                    try:
                        # read in JSON data
                        data = loads(fline)
                        
                        # check if JSON data conform to schema, return timestamp if checks passed
                        timestamp = conformity_checks(data, timestamp_upper, timestamp_lower)
                        
                        # update graph and calculate its median degree, write to file
                        G = update_graph(G, data, timestamp, maxtimestamp, timestamp_lower)
                        median_degree = median(G.degree().values())
                        results.write('{0:.2f}'.format(median_degree) + '\n')
                        
                        # update maxtimestamp
                        maxtimestamp = max(timestamp, maxtimestamp)
                        
                    except:
                        # data cannot be read in (malformed) or don't conform to schema
                        # median_degree exists, use it                        
                        if median_degree != None:
                            results.write('{0:.2f}'.format(median_degree) + '\n')
                        # no previous median_degree exists, write blank line to file
                        else:
                            results.write('\n')
                
                # if no input, write blank line to output file
                else:
                    results.write('\n')
    
    # close files
    f.close()
    results.close()


def conformity_checks(data, timestamp_upper, timestamp_lower):
    # check if all three keys present
    if all (key in data for key in ('created_time', 'actor', 'target')):

        # get Unix epoch timestamp
        timestamp = timegm(time.strptime(data['created_time'], '%Y-%m-%dT%H:%M:%SZ'))

        # check if values conform to schema via boolean masks
        mask_timestamp = (timestamp > timestamp_lower and timestamp < timestamp_upper)
        mask_actor = (type(data['actor']) == unicode and data['actor'].replace('-', '').replace('_', '').isalnum() and \
                     len(data['actor']) >= 5 and len(data['actor']) <= 25 and data['actor'][0].isalpha())
        mask_target = (type(data['target']) == unicode and data['target'].replace('-', '').replace('_', '').isalnum() and \
                      len(data['target']) >= 5 and len(data['target']) <= 25 and data['target'][0].isalpha())
        
        # all checks passed     
        if mask_timestamp and mask_actor and mask_target:
            return timestamp
        
        # one of the values does not conform to schema, throw exception
        else:
            raise ValueError('Values do not conform to schema.')
    
    # cannot find all three keys, throw exception
    else:
        raise ValueError('Keys missing.')


def update_graph(G, data, timestamp, maxtimestamp, timestamp_lower):
    # iff new entry also most recent (i.e. timestamp > maxtimestamp), check (& prune) edges and nodes
    # pruning not required if updating the graph for the first time (maxtimestamp == timestamp_lower)
    if (timestamp > maxtimestamp) and (maxtimestamp != timestamp_lower):
        
        # remove any outdated edges
        outdated = [(node1, node2) for node1, node2 in G.edges_iter()
                    if timestamp - 60 >= G.get_edge_data(node1, node2)['created_time']]
        G.remove_edges_from(outdated)
        
        # remove any disconnected (solitary) nodes
        disconnected = [node for node, degree in G.degree().items() if degree == 0]
        G.remove_nodes_from(disconnected)
    
    # add edge: if entry < 60s smaller than maxtimestamp and the edge does not exist
    # overwrite edge: if entry < 60s smaller than maxtimestamp and the edge does exist, but new one newer
    if (timestamp > maxtimestamp - 60) and \
       ((G.has_edge(data['actor'], data['target']) == False) or \
       (timestamp > G.get_edge_data(data['actor'], data['target'])['created_time'])):
        G.add_edge(data['actor'], data['target'], created_time = timestamp)
    
    # return updated graph
    return G


if __name__ == '__main__':
    main()
