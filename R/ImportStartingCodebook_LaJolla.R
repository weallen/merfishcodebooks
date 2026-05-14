ImportStartingCodebook_LaJolla<-function(v,k,t){
  
  #For any combination of v, k, and t, the function downloads and parses the equivalent lower bound from the La Jolla covering repository, as well as the method used to construct it.
  #Output is a list with the output table (Set-based) and the method as a string.
  
  
  library(rvest)
  #Download v-k-t-covering lower bound solution from the La Jolla Covering Repository
  url = paste("https://ljcr.dmgordon.org/cover/show_cover.php?v=",v,"&k=",k,"&t=",t,sep = "")  #Directly accesses the relevant covering.
  html <- read_html(url)  #The La Jolla Covering Repository returns a webpage for any possible url, even if no data exists.
  
  #Scrape table:
  html |> html_elements(xpath = "/html/body/pre/text()") -> data
  html |> html_elements(xpath = "/html/body/h2") -> method
  method = html_text(method)
  table = read.table(text=html_text(data))
  output= list(table,method)
  return(output)
  
}