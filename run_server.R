


library(plumber)

# Load the Plumber script
pr <- plumber::plumb('C:/Users/janko/python/proj_1/server_2.R')

# Start the Plumber server on a specified port
pr$run(port = 8001)
