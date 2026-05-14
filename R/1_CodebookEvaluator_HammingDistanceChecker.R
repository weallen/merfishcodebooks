HammingDistanceChecker <- function(
  #Required Arguments  
  Bits,  #Barcode Lengh. Nr of Decoding probes.
  InputFile, #Provide a csv-file to start the pipeline from. No header. If provided, will override other StartCodeSource. Can be either binary or set-based.
  Folder,
  CodeFolder = "C:\\Users\\Adameyko\\Desktop\\HammingCode batch runs\\RCodeLibrary",
  FileSep = " ", #Separator for reading the csv-file
  HW = 4, #Hamming Weight, Number of positive bits per code.
  MinHD = 4 #minimum Hamming Distance. minHD4 is equal to SECDED, Single-Error-Detection-Double-Error-Correction.
  
) {

  setwd(CodeFolder)

  source("ConvertSettoBinary.R")
  source("EvaluateCodebookHD.R")
  

## Load File
  File = paste(Folder,InputFile, sep = "")
  table = read.csv(File, sep = FileSep, header = FALSE) #Can be either binary or set-based. No header.
  
  if (max(table) == 1){BinaryOrSet = "Binary"} else {BinaryOrSet = "Set"}   
  length = nrow(table) 
  
## Convert to binary if needed  
  
  #Convert sets to binary if needed:
  if (BinaryOrSet == "Set"){
    Codes = ConvertBinarytoSet(table)
    
  } else {Codes = as.matrix(table)} #if starting set is already set based.
  
## Calculate  minHD of file   
    
  HD = EvaluateCodebookHD(Codes)

Rowconflicts = rowSums(HD < MinHD)
if (sum(Rowconflicts) == length){
  output = (paste("No conflicts detected, everything is in order")) 
  } else {output = (paste(sum(Rowconflicts)-length, " nr of Conflicts detected below the minHD requirement of ", minHD))  }

#graphical output unless the codebook is too large: 
if (nrow(HD)<1200){
heatmap(HD, scale = "none", Rowv = NA, Colv = NA)}

return(output)
}
