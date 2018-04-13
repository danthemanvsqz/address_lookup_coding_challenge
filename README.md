# Find Store

To run: `python find_store/find_store.py`

Tests: `python -m unittest tests`

I used libraries `geopy` for the geolocation and `docopt` to parse the command line. I used a simple 2D Euclidean math to calculate distance this will break down for large distances but should be good enough to find nearby stores. Alternatively we could use geopy's build in distance function. The logic is first find the lat long for the input, then traverse the input file and calculate the distance from the input and track the min distance. This algorithm will scale well and can be easily distributed across a cluster with litte refactoring.
