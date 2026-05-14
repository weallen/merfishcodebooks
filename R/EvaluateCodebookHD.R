EvaluateCodebookHD=function(Codes){
  length = nrow(Codes)
  HD = matrix(integer(0),nrow = length,ncol = length)
  
  for (i in 1:length){
    HD[i,] = rowSums((Codes + rep(Codes[i,], each = nrow(Codes))) %% 2)
  }
  return(HD)
}