ConvertSettoBinary <- function(SetCodebook, Bits = 0){

#Nr of Bits is identified by taking the max value of the provided Codebook. 
#OBS: if the starting codebook does not contain a code using the highest bit, Bits needs to to be provided as an argument. 
#Starting Codebook is supplied without a header.

if (Bits == 0){Bits = max(SetCodebook)}
length = nrow(SetCodebook)
Output = matrix(0,length, Bits)
for (i in 1:length){
  Output[i,as.integer(SetCodebook[i,])] = 1
}
return(Output)}  