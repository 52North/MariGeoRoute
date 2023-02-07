from routeparams import RouteParams

if __name__ == "__main__":
    filename = "/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/min_time_routeroute.json"
    rp_read = RouteParams.from_file(filename)
    rp_read.print_route()