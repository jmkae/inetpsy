library(plumber)
library(jsonlite)
library(graphicalVAR)

#* @post /computeVAR
function(df_json) {
  tryCatch({
    # Attempt to parse JSON
    df <- fromJSON(df_json)
    print("Data Frame Loaded:")  # Debug print
    print(df)  # Show the data frame in R console for verification
    df_prepared <- df$data
    # Run graphicalVAR
    result <- graphicalVAR(df_prepared, nLambda = 50, gamma = 0)
    print(result)
    corr_mat <- as.data.frame(result$PCC)
    print(corr_mat)
    
    # Convert the result to JSON and return
    jsonResponse <- toJSON(corr_mat)
    return(jsonResponse)
  }, error = function(e) {
    # Error handling: return an error message in JSON format
    return(toJSON(list(error = "An error occurred", message = toString(e$message))))
  })
}
