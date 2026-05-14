ConvertBinarytoSet <- function(BinaryCodebook){
  #Nr of Bits and length of codebook can always be calcualted and does not need to be provided.
  length = nrow(BinaryCodebook)
  HW = sum(BinaryCodebook[1,])
    
  SetCodebook = matrix(as.integer(0),length, HW)
  for (i in 1:length){
    SetCodebook[i,] = which(BinaryCodebook[i,] %in% 1)
  }
  return(SetCodebook)
}