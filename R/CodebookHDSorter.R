CodebookSorterWithStop <- function(
    #Arguments
  #Starting from a csv-file, either binary or set-based. The code will automatically identify which is provided.
  
  InputFile = "21Bit_HW5_HD4_finalsize1071Binary.csv",
  CodeFolder = "C:\\Users\\Adameyko\\Desktop\\HammingCode batch runs\\RCodeLibrary",
  InputFolder = "C:\\Users\\Adameyko\\Desktop\\HammingCode batch runs\\Rev2OutputNEW\\HW5",
  OutputFolder = "C:\\Users\\Adameyko\\Desktop\\HammingCode batch runs\\Rev2OutputNEW",
  FileSep = " ", #Separator for reading the csv-file
  Diagnostics = FALSE
  
) {
  
    setwd(CodeFolder)
  source("EvaluateCodebookHD.R")
  source("ConvertSettoBinary.R")
  ####################################
  ## Load File and calculate parameters
  ####################################
  File = paste(InputFolder,"/",InputFile, sep = "")
  if (!file.exists(File)){stop("File not Found. (Folder argument should not have a terminating /)")}
  table = read.csv(File, sep = FileSep, header = FALSE) #Can be either binary or set-based. No header.
  
  if (max(table) == 1){BinaryOrSet = "Binary"} else {BinaryOrSet = "Set"}   
  length = nrow(table) 
  
  #Convert sets to binary if needed:
  if (BinaryOrSet == "Set"){
    
    Codes = ConvertSettoBinary(table)
  } else Codes = as.matrix(table) #if starting set is already binary
  
  
  #Extract minHD and HW
  HW = sum(Codes[1,])
  MinHD = 4
  Bits = ncol(Codes)
  
  print(paste("Starting to reorder a codebook with HW =",HW,"and Barcode Length =",Bits)) 
  
  #########################################
  ## Calculate HD relationships of the file
  ## Created as a matrix of Hamming Distances with all codes versus all codes
  #########################################
  
  HD =EvaluateCodebookHD(Codes)
  #Check if minHD is correct
  Rowconflicts = rowSums(HD < MinHD)
  if (sum(Rowconflicts) == length){
    print(paste("No conflicts detected, everything is in order")) 
  } else {print(paste(sum(Rowconflicts)-length, " nr of Conflicts detected below the minHD requirement of ", minHD))  }
  
  ##########################################################################
  #Reorder Codebooks to maximize the HD from the start of the codebook. 
  ###########################################################################
  
  #########################################################################
  ##Step 1. Find a set of Codes that use as many Bits as possible with no overlap as the starting position.
  ##########################################################################
  
  NrWanted = floor(Bits/HW)
  iteration = 1
  
  CodesReorder = Codes
  FailedtoFind = TRUE
  while (TRUE){  #Reset point if the below loop fails to find a group large enough
    iteration = iteration + 1
    if (iteration > 300){print(paste("Failed to find a full minHD group, turning to random methods"));FailedtoFind = TRUE; break}
    CodesReorder[,] = 0
    RandomStart = sample.int(nrow(Codes),1)
    CurrentCodeIndexes = RandomStart
    CodesReorder[1,] = Codes[RandomStart,]
    CodesBreakdown = Codes
    row = 2
    while (TRUE){
      UsedBits = as.logical(colSums(CodesReorder))
      CodesBreakdown = Codes[,!UsedBits]
      CodeBreakdownSums = rowSums(CodesBreakdown)
      Choices = which(CodeBreakdownSums==HW)
      if (length(Choices)>0){
        NextCodeIndex = Choices[sample.int(length(Choices),1)]
        CurrentCodeIndexes = c(CurrentCodeIndexes,NextCodeIndex)
        CodesReorder[row,] = Codes[NextCodeIndex,]
        
        if (row == NrWanted){Done = TRUE; break} else {row = row + 1}
      } else {Done = FALSE; break}
    }
    if (Done == TRUE){
      print(paste("Found a full minHD group after ", iteration, "iterations. Continuing with random fill-in choosing minimum average HD codes."))
      FailedtoFind = FALSE
      break
    }
  }
  
  #Prepare a HD matrix for analyzing which row to add next
  HDforReorder = HD; 
  HDforReorder[HDforReorder == 0] <- -1000000 #Adding a penalty value to main diagonal to prevent a code being chosen twice.
  
  
  if (FailedtoFind == TRUE){
    ## One iteration of the below loop is started
    CodesReorder = Codes
    CodesReorder[,] = 0
    RandomStart = sample.int(nrow(Codes),1)
    HD_Start= HD[RandomStart,]
    CurrentCodeIndexes = RandomStart
    CodesReorder[1,] = Codes[RandomStart,]
    ##First Iteration
    HDSums=HDforReorder[,CurrentCodeIndexes]
    Choices = which(HDSums==max(HDSums))
    NextCodeIndex = Choices[sample.int(length(Choices),1)]
    CurrentCodeIndexes = c(CurrentCodeIndexes,NextCodeIndex)
    CodesReorder[2,] = Codes[NextCodeIndex,] 
    CurrentRow = 3
  } else {
    CurrentRow = NrWanted+1  
  }
  
  #######################################
  #Continue with adding random codes with the highest possible combined HD to all previous rows. 
  #######################################
  
  #Define Limit when no more need to reorder (When the max HD of the next code has reached or surpassed the average)
  
   HDLimit = sum(HD)/(nrow(HD)-1)/(ncol(HD)) #The average value in the HD matrix not counting 0s
  #Reorder the remaining Codes by iteratively choosing the one with the lowest overlap to bits used by earlier codes.
  NrOfCodesReordered = nrow(Codes) #will be replaced with the actual value if limit is reached.
  BelowAverageCodes = 0
  while (TRUE){
    #Sum up the rows of HDforreorder, but only matching the columns already used. Since the main diagonal has a penalty value, it will never be picked.
    HDSums=rowSums(HDforReorder[,CurrentCodeIndexes])
    #Select choices from among all codes with the highest combined HD against all current rows
    MaxHDSums = max(HDSums)
    #Once 5 codes have been added with a HD to the previous rows that is lower than the average for the original codebook, the code terminates early and adds the rest of the codes back in.
    if (MaxHDSums/(CurrentRow-1)<=HDLimit){
      BelowAverageCodes = BelowAverageCodes+1
      if (BelowAverageCodes >=5){
      CodesReorder[CurrentRow:nrow(Codes),] = Codes[-CurrentCodeIndexes,]
      NrOfCodesReordered = CurrentRow-1
      print(paste("Ending reordering at row",NrOfCodesReordered, "as HD has reached average."))
      break
      }
      
    }
    Choices = which(HDSums==max(HDSums))
    #Randomize a choice
    NextCodeIndex = Choices[sample.int(length(Choices),1)]
    #Add it to list of codes used, and to the reordered Codebook
    CurrentCodeIndexes = c(CurrentCodeIndexes,NextCodeIndex)
    CodesReorder[CurrentRow,] = Codes[NextCodeIndex,] 
    #Check if finished.
    if (CurrentRow == length){break}
    CurrentRow = CurrentRow + 1
  }
  
  ##Recalculate HD relationship to verify minimumHD
  
  HD_Reordered = EvaluateCodebookHD(CodesReorder)
  Rowconflicts = rowSums(HD_Reordered < MinHD)
  if (sum(Rowconflicts) == length){
    print(paste("After reordering, no conflicts detected, everything is in order")) 
  } else {print(paste("After reordering, ",sum(Rowconflicts)-length, " nr of Conflicts detected below the minHD requirement of ", minHD))  }
  if (nrow(table) != nrow(CodesReorder)){print(paste("Something went wrong, final codebook not same length as original"))}
  
  ####################
  ## Output
  ####################
  
  setwd(OutputFolder)
  filetest = sub('\\.csv$', '', InputFile) 
  filename = paste(sub('\\.csv$', '', InputFile),"_reordered",NrOfCodesReordered,".csv",sep="")
  write.table(CodesReorder,filename, row.names = FALSE, col.names = FALSE)
  
  ##############################################################
  #Various diagnostics and heatmaps to show how long the early stretch with high average HD is. Recommended to not use unless manually inspecting results.
  ##############################################################
  if (Diagnostics == TRUE){
    AverageHDReordered = rep(0,length)
    for (i in 2:length){
      AverageHDReordered[i]=mean(HD_Reordered[i,1:i-1])
    }
  }
  
  #ggplot() + geom_line(aes(x=1:length,y=AverageHDReordered))
  
  #Original HDs
  #if (nrow(HD)<1200){
  #  heatmap(HD, scale = "none", Rowv = NA, Colv = NA)}
  #if (nrow(HD)<1200){
  #  heatmap(HD_Reordered, scale = "none", Rowv = NA, Colv = NA)}
  
  ################################################################################
  ##Comparison to random shuffling to validate the method and quantify usefulness (Inactivated, but can be used to manually look into  specific code reordering in detail)
  ################################################################################
  
  #To avoid adding the same code twice without disrupting indexing, the codes already used are penalized.
  ##First Iteration
  
  #CodesRandom=Codes[sample(nrow(Codes)),]
  #HD_Random = matrix(integer(0),nrow = length,ncol = length)
  #for (i in 1:length){
  #  HD_Random[i,] = rowSums((CodesRandom + rep(CodesRandom[i,], each = nrow(CodesRandom))) %% 2)
  #}
  #RandomAverageHD = rep(0,length)
  #for (i in 2:length){
  #  RandomAverageHD[i]=mean(HD_Random[i,1:i-1])
  
  #}
  
  #ggplot() + geom_line(aes(x=1:length,y=AverageHDReordered), color = "purple") + geom_line(aes(x=1:length,y=RandomAverageHD), color = "darkgreen")
  #ggplot() + geom_line(aes(x=1:round(length*0.1),y=AverageHDReordered[1:round(length*0.1)]), color = "purple") + geom_line(aes(x=1:round(length*0.1),y=RandomAverageHD[1:round(length*0.1)]), color = "darkgreen")
  #ggplot() + geom_line(aes(x=1:round(length*0.1),y=AverageHDReordered[1:round(length*0.1)]), color = "purple", size = 3) + geom_line(aes(x=1:round(length*0.1),y=RandomAverageHD[1:round(length*0.1)]), color = "darkgreen", size = 3) + ylim(HW,HW*2) + theme_bw()
  #ggplot() + geom_line(aes(x=1:round(length),y=AverageHDReordered[1:round(length)]), color = "purple", size = 1) + geom_line(aes(x=1:round(length),y=RandomAverageHD[1:round(length)]), color = "darkgreen", size = 1) + ylim(HW,HW*2) + theme_bw()
  
  #heatmap(HD_Reordered[1:50,1:50], scale = "none", Rowv = NA, Colv = NA)
  #heatmap(HD_Random[1:50,1:50], scale = "none", Rowv = NA, Colv = NA)
  
  
  
}
