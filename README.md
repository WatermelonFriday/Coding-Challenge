# Insight Data Engineering Coding Challenge (Python 2.7)

# Documentation

## Intro
I used one non-standard Python module, networkx (v1.11), which can be installed using `pip install networkx`. Other standard modules used were `numpy`, `sys`, `time`, `calendar` and `json`.

## Performance
The code can process the sample file containing roughly 1800 JSON complete entries in around 0.35 seconds on a 2012 Lenovo T430s with 8GB of RAM and no SSD.

## Structure of the code
The code is essentially composed of three functions: `main(.)`, `conformity_checks(.)` and `update_graph(.)`.

### main(.)
- Initializes the empty graph and the auxilliary time objects required for the computation of the 60-second rolling window.
- Lazily reads in rows of data and writes results to the output file line-by-line.
- Contains the code dealing with converting lines of text ("JSON Line" entries) into Python dicts (see below for details).
- Once a complete JSON entry is successfully read in, the code checks the conformity of keys and values with the "schema".
- It then updates the graph, calculates its median degree and writes the result to the output file.
- Finally, it updates the timestamp of the most recent edge in the graph which facilitates the 60-second window analysis.

My underlying assumption is that the JSON entries typically conform to the JSON (i.e. JSON Line) standard. That is, all keys are wrapped in double quotes and all string values are wrapped in double quotes (not required for numbers, booleans, missing values, etc.). An exception from this are deviations that show up as either blank lines and/or incomplete entries:

1. If an input line is blank after stripping out the whitespaces (this includes \n, \r\n and \r characters), the code inserts a blank line in the output file.

2. If the input row is not blank but at the same time also does not conform to the JSON standard (i.e. is either malformed or incomplete) or does not conform to the "schema" used for this exercise (see below), the data in that row are *not* used in the computation of the median degree. Instead, the median degree of the previous iteration is written to the output file (i.e. the graph is not updated). The only exception to this rule is when the median degree has not yet been calculated, e.g. if the first row of the input file is malformed; in that case, empty lines are inserted in the output file until the first time a complete JSON entry allows for a successful computation of the median degree.

3. This way, the output file will always have the same number of rows than there are input lines (i.e. lines terminated by either \r, \n, or \r\n in the input file).

### conformity_checks(.)
In the context of this exercise, "schema" is a loosely defined combination of three keys & values. For the JSON entry to pass these checks, it needs to have all three key-value pairs.

Further, the timestamp of each entry must be based on the `%Y-%m-%dT%H:%M:%SZ` datetime mask. Also, timestamps cannot be from before the time Venmo was founded (April 2009 as per http://www.crunchbase.com/organization/venmo) and are bounded above by the current time. Any other datetime format that does not adhere to the above mask is considered invalid; same goes for timestamps outside of the allowed range. In these cases, the timestamp check fails, the entry is skipped and the median degree of the previous iteration of the graph (or a blank line) is written to the output file.

Actor and target (collectively, username) values must conform to the patterns observed in the sample data and when logged in one's Venmo online profile. This means that usernames can only be alphanumeric strings between 5 and 25 (incl.) characters long, and have to start with a letter. The only two other characters allowed are "-" (dash) and "_" (underscore).

If the JSON entry passes all checks, the timestamp calculated is returned to the main function to avoid computing it twice and then the code moves on to updating the graph. If the entry fails at least one test, the median degree of the previous iteration is written to the file (subject to the first-entry exception).

### update_graph(.)
Upon successfully reading in the entry, the function inspects if the new entry is more recent that the most recent existing entry. If so, some edges and nodes might have to be removed. This is done only after at least one edge has already been added to the graph.

Once the graph has been pruned, the new edge is added to the graph if up to 60 seconds older than the most recent edge and if another edge between the same two nodes does not yet exist. If such an edge does already exist, the code checks if the new edge is newer (more recent) than the existing one and if it falls in the 60-second window. If so, it overwrites the existing edge; if not, it discards it. Likewise the edge is discarded if it falls outside of the 60-second window.

Once the graph is updated it is returned to the main function so that its median degree can be calculated and the result written to the output file.

## Miscellaneous
The code has also been tested on a CentOS 6.7 server running Python 2.6 (in which case the networkx v1.9 had to be installed by running `pip install -Iv https://pypi.python.org/packages/source/n/networkx/networkx-1.9.tar.gz`).

The code could be further sped up by using graph libraries written in C/C++ but with Python bindings (such as `graph-tool`, `python-igraph` or `NetworKit`). However, I thought the current implementation using networkx was fast enough for the case at hand.
