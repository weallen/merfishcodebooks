PruningToConformToMinHD <-function(HD, Codes){
  
  #The ConflictLevel denotes what level of interconnected networks of HD-breaking codes exists.
  #Conflict Level 1: Linear networks
  #Conflict level 2:
  Rowconflicts = colSums(HD == 2)
  tempCodes = Codes  
  PruningIteration = 0
  ConflictLevel = -1
  
  #Putting aside all non-conflicting rows to save memory.
  ZeroesLeftAside = FALSE
  if (0 %in% Rowconflicts & sum(Rowconflicts) >2){    #The second check handles a very unusual case where there is only one conflict to deal with.
    ZeroConflictCodes = Codes[Rowconflicts==0,]
    Codes = Codes[Rowconflicts!=0,]
    HD = HD[Rowconflicts!=0,Rowconflicts!=0]
    ZeroesLeftAside = TRUE
  }
  
  HD_bin = matrix(FALSE,nrow=nrow(HD),ncol=ncol(HD))
  HD_bin[HD==2]=TRUE
  
  
  while (TRUE){
    PruningIteration = PruningIteration +1
    if (PruningIteration %% 5 == 0 ){
      print(paste("Pruning in progress, iteration nr ",PruningIteration,". Conflict level is ",ConflictLevel, sep = ""))
    }
    
    #Start by recalculating Conflict diagrams.
     Rowconflicts = colSums(HD_bin)  #colSums is quicker on large matrices.
    
    #Check if we are done
    if (sum(Rowconflicts)==0){
      break
    }
    
    #Measure Complexity of conflicting networks
    ConflictLevel = max(Rowconflicts, na.rm=TRUE)
    
    #Rule 1: Any neighbour of a 1 can always be deleted.
    # Find first 1 in conflict table. Delete its neighbour. 
    if (1 %in% Rowconflicts){
      
      
      RowtoDelete = match(TRUE,HD_bin[match(1,Rowconflicts),])
      Codes = Codes[-RowtoDelete,]
      HD_bin = HD_bin[-RowtoDelete,-RowtoDelete] #Deleting both row and column associated with the RowToDelete.
      next
    }
    
    
    
    #Rule 2a: Break up simple loops (If ConflictLevel = 2 and no 1s exists, the only configuration is circular linear loops):
    if (ConflictLevel == 2 ){   #A conflict level of 2 with no 1s means there are only simple loops. Delete the first 2 2.
      
      RowtoDelete = match(2,Rowconflicts)
      Codes = Codes[-RowtoDelete,]
      HD_bin = HD_bin[-RowtoDelete,-RowtoDelete]
      next
    }
    
    #Rule 2b: Find a "loose triangle" (a 2 with 2 neighbours). Delete both neighbours if they are themselves conflicting
    #Reasoning: Out of 3 interconnected codes, 2 will utimately need to be deleted. If one of the three only has conflicts with the other two (ConflictLevel 2), deleting both of the others will always retain the highest total number as saving one of the others could potentially conflict with other codes.
    if (2 %in% Rowconflicts){  #In super special subcases, there are no 2s but still higher conflicts.
    
    
    #Generate coordinates to all conflicts
    ConflictIndexes = which(arr.ind = TRUE, HD_bin)
    ConflictIndexespaste = paste(ConflictIndexes[,1],"_",ConflictIndexes[,2], sep ="")
    
    #Generate coordinates of all pairs of codes that are linked to any 2s
    #The below code has a specific subcase where only one single pair is available for checking, as the reshape function will struggle without columns. 
    
    
      RowConflict2List = which(Rowconflicts == 2)
    
    if(length(RowConflict2List)>1){
      Conflict2Indexes = which(arr.ind=TRUE,HD_bin[RowConflict2List,])
      
      Conflict2Indexes = Conflict2Indexes[order(Conflict2Indexes[,"row"]),]
      
      Conflict2IndexesReshaped = matrix(0,nrow=nrow(Conflict2Indexes)/2, ncol=2)
      Conflict2IndexesReshaped[,1] = Conflict2Indexes[seq(1,nrow(Conflict2Indexes),2),2]
      Conflict2IndexesReshaped[,2] = Conflict2Indexes[seq(2,nrow(Conflict2Indexes),2),2]
      #Conflict2IndexesReshaped = reshape(within(as.data.frame(Conflict2Indexes), q <- ave(seq_along(row), row, FUN = seq_along)), direction = "wide", idvar = "row", timevar = "q")[,2:3]
      
      
      Conflict2Indexespaste = paste(Conflict2IndexesReshaped[,1],"_",Conflict2IndexesReshaped[,2], sep ="")
      
      #If both links are also conflicting, both can be safely deleted.
      RowConflict2ListTriangles = (Conflict2Indexespaste %in% ConflictIndexespaste)
      
      if (sum(RowConflict2ListTriangles) >0){
        
        #Delete both self-conflicting neighbours next to a loose 2
        PotentialDeletions = which(RowConflict2ListTriangles)
        #Randomize which pair to delete.
        
        RowsToDelete = Conflict2IndexesReshaped[PotentialDeletions[sample(length(PotentialDeletions),1)],]
        Codes = Codes[-RowsToDelete,]
        HD_bin = HD_bin[-RowsToDelete,-RowsToDelete]
        next 
      }
      
    }
    else {
      Conflict2Indexes = which(HD_bin[RowConflict2List,])
      Conflict2Indexespaste = paste(Conflict2Indexes[1],"_",Conflict2Indexes[2], sep ="")
      if(Conflict2Indexespaste %in% ConflictIndexespaste){
        RowsToDelete = Conflict2Indexes
        Codes = Codes[-RowsToDelete,]
        HD_bin = HD_bin[-RowsToDelete,-RowsToDelete]
        next 
      }
    }
    }
  
    
    #If no Rules hit above, delete a code with the highest conflict level
    RowtoDelete = match(ConflictLevel,Rowconflicts)
    Codes = Codes[-RowtoDelete,]
    HD_bin = HD_bin[-RowtoDelete,-RowtoDelete]
    next
    
    
  }
  
  
  if (ZeroesLeftAside == TRUE){
   Codes = rbind(ZeroConflictCodes,Codes)
  }
  Codes = Codes[sample(nrow(Codes)),]
  
  #Output of pruning      
  NrRemoved = nrow(tempCodes)-nrow(Codes)
  NrAfterPruning = nrow(Codes)
  OutputCodes = Codes
  output = list(NrRemoved,NrAfterPruning,OutputCodes)
  return(output)
}