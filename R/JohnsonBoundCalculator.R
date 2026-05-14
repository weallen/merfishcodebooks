JohnsonBoundCalculator<-function(v,k,MinHD){
  
  w = k
  d = MinHD
  n = v
  e = ceiling(d/2)
  
  JohnsonStart = n-w+e
  MaxJohnson = 1
  for (Johnson in JohnsonStart:n){
    MaxJohnson = floor(MaxJohnson*(Johnson*1/(Johnson-n+w)) + 0.000001) #The addition of .000001 is necessary to avoiding flooring a multiplication of 0.33333*3, for example n=56,d=4,w=4.
  }
  return(MaxJohnson)
}