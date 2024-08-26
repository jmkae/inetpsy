

library(plumber)
library(graphicalVAR)

#* @param df_json JSON string of the DataFrame
#* @post /computeVAR


#* Accepts a POST request with JSON body containing the data
#* @post /computeNetwork
function(req) {
  df_json <- req$postBody
  data <- fromJSON(df_json)$df_json
  # process the data...
  return(toJSON(data))  # Sending back data or a result for simplicity
}


function(df_json) {
  df <- jsonlite::fromJSON(df_json)
  result <- graphicalVAR(df, nLambda = 50, gamma = 0)
  jsonlite::toJSON(as.matrix(result[[1]]))
  print(df)
}





