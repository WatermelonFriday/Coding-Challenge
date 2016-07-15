# Insight Data Engineering Coding Challenge

## Documentation

The solution has been implemented in Python 2.7. I used two non-standard Python modules, numpy and networkx (v1.11). The latter can be installed using "pip install networkx", while the former is usually a part of scientific Python distributions like Anaconda. Other modules used were sys, time, calendar and json.

The code is essentially composed of three functions:

### main(.)

Initializes the empty graph and the auxilliary time objects required for the computation of the 60-second rolling window. Also lazily reads in rows of data and writes results to the output file line-by-line. Additionally, this function contains the code dealing with converting lines of text (JSON Line entries) into Python dicts. Once a complete JSON entry is successfully read in, the code checks the conformity of keys and values with the schema, updates the graph, calculates the median degree of the updated graph and then writes the result to the output file. Finally, it updates the timestamp of the most recent edge in the graph which facilitates the 60-second window analysis.

The underlying assumption here is that the JSON entries under normal circumstances conform to the JSON (i.e. JSON Line) standard. That is, all keys are wrapped in double quotes and all string values are wrapped in double quotes (not required for numbers, booleans, missing values, etc.). Deviations show up as either blank lines and/or incomplete entries.

That is, if an input line is blank after stripping out the whitespaces (this includes \n, \r\n and \r characters), the code inserts a blank line in the output file. If, on the other hand, the input row is not blank but at the same time also does not conform to the JSON standard (i.e. is either malformed or incomplete) or does not conform to the "schema" used for his exercise (see below), the data in that row are *not* used in the computation of the median degree; instead, the median degree of the previous iteration is written to the output file (essentially, the graph is not updated). This way, the output file will always have the same number of rows than there are input lines (i.e. lines terminated by either \r, \n, or \r\n in the input file). The only exception to this rule is when the median degree has not yet been calculated, e.g. if the first row of the input file is malformed; in that case, empty lines are inserted in the output file until the first time a complete JSON entry allows for a successful computation of the median degree.

### conformity_checks(.)

In the context of this exercise, "schema" is a loosely defined combination of three keys and values. For the JSON entry to pass the conformity checks, it needs to have all three keys.

Further, the timestamp of each entry must be based on the '%Y-%m-%dT%H:%M:%SZ' datetime mask. Also, timestamps cannot be from before the time Venmo was founded (April 4, 2009 as per http://www.crunchbase.com/organization/venmo) and are bounded above by the current time. Any other datetime format that does not adhere to the above mask is considered invalid; same goes for timestamps outside of the allowed range. In these cases, conformity checks fail, the entry is skipped and the median degree of the previous iteration of the graph is written to the output file.

Actor and target (collectively, username) values must conform to the patterns observed in the sample data and when logged in one's Venmo profile. This means that usernames can only be alphanumeric strings between 5 and 25 (incl.) characters long, and have to start with a letter and not a digit. The only two other characters allowed are "-" (dash) and "_" (underscore).

If the entry passes all checks, the timestamp calculated for the timestamp is returned to the main function to avoid computing it twice and then the code moves on to updating the graph. If the entry fails at least one test, the median degree of the previous iteration is written to the file.

### update_graph(.)

Upon successfully reading in an individual entry, the function first inspects if the new entry is more recent that the most recent existing entry. If so, some edges and nodes might have to be removed, so it checks the edges and removes them if necessary. After that it also checks if there are any newly-disconnected nodes and removes them. This is not done when the first edge is added to the graph.

Once the edges and the nodes have been potentially pruned, edges are added to the graph if up to 60 seconds older than the most recent edge and an edge between the same two nodes does not yet exist. If such an edge already exists, the code checks if the new edge is newer (more recent) than the existing one and if it falls in the 60-second window. If so, it overwrites the existing edge; if not, it discards it. Likewise the edge is discarded if it falls outside of the 60-second window.

Once the graph is updated it is returned to the main function so that its median degree can be calculated and the results written to the output file.

## Miscellaneous

The code has been also tested on a CentOS 6.7 server running Python 2.6 (in which case the 1.09 version of the networkx module has to be installed by running "pip install -Iv https://pypi.python.org/packages/source/n/networkx/networkx-1.9.tar.gz").

The code could be further sped up by using graph libraries written in C/C++ but with Python bindinds (such as graph-tool, igraph or NetworKit). I thought the current implementation using networkx was fast enough for the case at hand.
