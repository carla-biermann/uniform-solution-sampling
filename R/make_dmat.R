library(sf)

#read in line file
paths <- read_sf("spatial_data/MSP_CairngormConnect.shp")

#make a 'focal point'
mid_point <- st_as_sf(data.frame(X = -410000, Y = 7795000), coords = c("X","Y"))
st_set_crs(mid_point, st_crs(paths))


#plot the data
plot(paths$geometry, col = "grey")
plot(mid_point, add=TRUE, pch=16)


#now sample the line path network
dens <- 1/100 # 1 point per 100m
path_locs <- st_line_sample(x = paths, density = 1/100, type = "regular")


#trim the area around center point
buffer_width <- 5000 #defines the buffer width around mid_point to clip paths (m)
mid_point_buff <- st_buffer(mid_point, dist = buffer_width)


#plot the data
plot(mid_point_buff, add=TRUE, col = adjustcolor("navy", 0.2))


#select points inside buffer
path_locs_in <- st_crop(path_locs, st_bbox(mid_point_buff))

plot(path_locs_in, add=TRUE, col = "red", pch=".")

dmat <- st_distance(path_locs_in)

#save this as something usable
