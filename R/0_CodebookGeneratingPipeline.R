ErrorRobustCodebookGeneratorPunct <- function(
    
  #Required Parameters: Bits, CodeFolder, Outputfolder, and 1 out of the 5 starting points described below.
  Bits,  #Barcode Lengh. Nr of Decoding probes.
  CodeFolder = "C:\\Users\\Adameyko\\Desktop\\HammingCode batch runs\\RCodeLibrary",
  Outputfolder = "C:\\Users\\Adameyko\\Desktop\\HammingCode batch runs\\Rev2Output",  #C:\\Users\\ASSIGNED_OUTPUTFOLDER_HERE. Outputs are two csv-files (Binary and Set) as well as a metadata file. 
  
  #Hamming Code Parameters
  HW = 4, #Hamming Weight, Number of positive bits per code.
  MinHD = 4, #minimum Hamming Distance. minHD4 is equal to SECDED, Single-Error-Detection-Double-Error-Correction.
  
  FilenameOverride = FALSE, #Will override the automatic filenameprefix with a custom filename prefix. Do not include file format. Example: FilenameOverride = "Examplefilename" 
  
  #####################
  #Starting Points:
  #####################
  #There are five starting points
  #Only one of these five should be set to its input parameter or TRUE, the other 4 should be set to FALSE.
  
  ###Start 1:
  FreshStart = FALSE,  #If TRUE, starts with an empty matrix instead of a starting point.
  
  ###Start 2:
  CustomStartingFile = FALSE, #If a csv.file, Provide a csv-file to start the pipeline from. No header. Can be either binary or set-based.
  CustomStartingFileSep = " ", #Separator for reading the csv-file
  
  ###Start 3:
  StartWithCoveringDesign = FALSE, # If TRUE, uses a La Jolla repository covering design from the same parameter combination. 
  
  ###Start 4:
  PunctureSpecificCoveringStart = FALSE, #If a number is provided, Start with Specific higher-level v,k,t-covering design to puncture, with higher number of Bits. Inputs is Bits.
  
  ###Start 5:
  PunctureCoveringRange = FALSE, #If TRUE, Searches through covering designs higher than the Barcode Length of the wanted codebook. Performs pruning and then chooses the largest one to continue processing.
  RangeUpperLimit = 0, #hen Puncturing a range of covering theory lower bounds, this parameter sets the highest point. Expressed as the barcode length of the highest wanted search. Defaults to one v higher if no argument given.
  
  ################
  #Stop conditions
  ################
  
  maxIterations = 300,   #How long to look for improvements. Resets after every improvement.
  dynamicMaxIterations = TRUE,  #Resets the maxIterations counter every time codebook increases in size.
  CandidateCutoff = 1  #Minimum number of candidates to continue. Recommended to keep at 1. See "candidates" lower down.
) {
  
  #For testing: Bits = 24; HW = 5; MinHD = 4; StartWithCoveringDesign = TRUE; PunctureCoveringRange = FALSE; PunctureSpecificCoveringStart = FALSE; RangeUpperLimit = 21; CodeFolder = CodeFolder = "C:\\Users\\Adameyko\\Desktop\\HammingCode batch runs\\RCodeLibrary"; Outputfolder = "C:\\Users\\Adameyko\\Desktop\\HammingCode batch runs\\Rev2Output"; maxIterations = 300; dynamicMaxIterations = TRUE; FreshStart = FALSE; CandidateCutoff = 1; MinimizeOutput = TRUE; FilenameOverride = FALSE; CustomStartingFile = FALSE; CustomStartingFileSep = " "
  
  
  #STRATEGY
  #1. Calculate Theoretical Maximum using the Johnson Bound Equation.
  #To be used to estimate how close to maximum potential we are at at any stage.
  
  #2. Starting Codebook.
  #Either download an elegant starting point or start fully fresh using the FreshStart=TRUE argument.
  #vkt-coverings from the LaJOlla covering repository are 100% optimized for any Bit size with mod 6 = 2or4 (for HW4,minHD2) and are usually a good starting point for many other combinations.    #Any csv.file can also be used as a starting point, either in set-based from or in binary. Does not need to fulfil minHD requirements, will be pruned instead.
  
  #3. Pruning
  #If the Seeding Code Set is not compliant with the minHD argument, it will be pruned in the way that salvages the longest Starting Codebook possible (deterministic up until the third conflict level, see below)
  #The code automatically checks if pruning is needed
  
  #4. Scavenging: Iterative Set Exchange Loop
  #If the Code Set is not already at 100% Theoretical Maximum, it will scavenge for increases to the Code Set size using analysis of t-sets (smaller sets which make up the codes (k-sets) and which have to be unique in the Code Set)
  #Scavenging is run for a number of predetermined iterations without any change in codebook length, or until it reaches 100% capability, or if it runs out of t-set clusters (candidates).
  
  #4. Output
  #The Code Set is outputted in both binary and in Set format, accompanied by a text file with metadata about how it was generated.
  
  
  ######################################
  ## Initialization and mathematical definitions  
  ######################################
  setwd(CodeFolder)
  source("ConvertBinarytoSet.R")
  source("ConvertSettoBinary.R")
  source("EvaluateCodebookHD.R")
  source("ImportStartingCodebook_LaJolla.R")
  source("IterativeSetExchangeLoop.R")
  source("JohnsonBoundCalculator.R")
  source("PruningToConformToMinHD.R")
  
  setwd(Outputfolder)
  library(rvest)
  library(dplyr)
  
  if (FreshStart == TRUE){Strategy = "FreshStart"}
  if (CustomStartingFile != FALSE){Strategy = "CustomStartingFile"}
  if (StartWithCoveringDesign == TRUE){Strategy = "StartWithCoveringDesign"}
  if (PunctureCoveringRange == TRUE){Strategy = "PunctureCoveringRange"}
  if (PunctureSpecificCoveringStart != FALSE){Strategy = "PunctureSpecificCoveringStart"}
  
  StartTime = Sys.time() 
  
  #Converting to covering nomenclature.
  v = Bits
  k = HW
  a = MinHD/2-1
  t = k-a  
  
  ######################################
  ## Calculating Upper Bound (Theoretical Maximum) using Johnson Bound
  ######################################
  
  TheoreticalMax = JohnsonBoundCalculator(v,k,MinHD)
  
  ######################################
  ## Starting Option 1: Fresh Start
  ######################################
  
  if (FreshStart == TRUE){Codes = matrix(); OutputCodes = Codes}  else {  
    
    ######################################
    ## Starting Option 2: Custom Starting Codebook (Supplied as a .csv-file)
    ######################################  
    
    if (CustomStartingFile != FALSE){
      
      table = read.csv(CustomStartingFile, sep = CustomStartingFileSep, header = FALSE) #Can be either binary or set-based. No header.
      
      ##Identify if user-supplied starting codebook is set-based or in binary:
      if (max(table) == 1){CustomStartisBinary = TRUE} else {CustomStartisSetbased = TRUE} 
    }
    
    
    ######################################
    ## Starting Option 3: La Jolla Covering Lower Bound Start 
    ######################################  
    
    else if (StartWithCoveringDesign == TRUE){  
      
      ImportLaJolla = ImportStartingCodebook_LaJolla(v,k,t)
      table = ImportLaJolla[[1]]
      method = ImportLaJolla[[2]]
    }
    
    ######################################
    ## Starting Option 4: La Jolla Covering Lower Bound Start with puncturing at a specific higher-length.
    ######################################  
    
    else if (PunctureSpecificCoveringStart != FALSE){
      PuncturedCoveringStartingPoint = PunctureSpecificCoveringStart
      print(paste("Checking vkt-covering for v equal to ",PunctureSpecificCoveringStart))
      ImportLaJolla = ImportStartingCodebook_LaJolla(PunctureSpecificCoveringStart,k,t)
      tableplus = ImportLaJolla[[1]]
      method = ImportLaJolla[[2]]
      MaxUsedBit = apply(tableplus[,], 1, max)
      table = tableplus[MaxUsedBit <= v,]
    }
    
    ######################################
    ## Starting Option 5: La Jolla Covering Lower Bound Start evaluating all alternative starts up until the nearest Steiner System. 
    ######################################  
    #Puncture Steiner Starts: Evaluates all covering designs up until a provided maximum. No need to increase this higher than the nearest Steiner System       and often works best exactly one above. Whichever has the highest codebook size after purning is kept. 
    
    else if (PunctureCoveringRange == TRUE){
      
      ## Download and evaluate (v,k,t)-covering lower bounds both from the Barcode Length that is checked, but also with higher v-s until the provided Upper Limit. Retain the codebook with the highest size.
      PuncturingRangeResults = 0
      if (RangeUpperLimit == 0){RangeUpperLimit = Bits+1} 
      TempStoragePrunedResults = list()
      NrafterPruningSave= list()
      FilteringNeededSave= list()
      NrRemovedSave= list()
      methodSave = list()
      for (vplus in v:RangeUpperLimit){
        
        ##Download
        print(paste("Checking vkt-covering for v equal to ",vplus))
        
        ImportLaJolla = ImportStartingCodebook_LaJolla(vplus,k,t)
        tableplus = ImportLaJolla[[1]]
        methodSave[[vplus]] = ImportLaJolla[[2]]
        MaxUsedBit = apply(tableplus[,], 1, max)
        table = tableplus[MaxUsedBit <= v,]
        length = nrow(table) 
        tCodes = ConvertSettoBinary(table)
        Codes = tCodes
        ##Check for pruning
        HD = EvaluateCodebookHD(Codes)
        Rowconflicts = rowSums(HD == 2)
        ##Prune
        
        if (sum(Rowconflicts) > 0){
          
          #Calculate nr of conflicts per row
          print(paste("Evaluating truncated version of v =", vplus,". Pruning Conflicts"))
          PruningOutput = PruningToConformToMinHD(HD,Codes)
          NrRemoved = PruningOutput[[1]]
          NrAfterPruning = PruningOutput[[2]]
          OutputCodes = PruningOutput[[3]]
          Codes = OutputCodes
          
          print(paste("After pruning the yield is ", nrow(Codes)," equal to ", round(nrow(OutputCodes)/TheoreticalMax*100,1),"% of Theoretical Maximum",sep = ""))
          FilteringNeeded = "Yes"
        } else {
          print(paste("Evaluating a truncated version of v =", vplus,". No conflicts, yield is ", round(nrow(tCodes)/TheoreticalMax*100,1),"% of Theoretical Maximum",sep = ""))
          OutputCodes = Codes
          NrAfterPruning = NA
          FilteringNeeded = "No"
          NrRemoved = "None"
        }
        
        ##The size, codebooks, and metadata are temporarily stored awaiting decision on which one to continue with 
        PuncturingRangeResults[vplus] = nrow(OutputCodes)
        TempStoragePrunedResults[[vplus]]= OutputCodes
        NrafterPruningSave[[vplus]] = NrAfterPruning
        FilteringNeededSave[[vplus]] = FilteringNeeded
        NrRemovedSave[[vplus]] = NrRemoved
        
      }
      #Choosing a starting point
      PuncturedCoveringStartingPoint = which.max(PuncturingRangeResults)
      #Handling metadata, saving the metadata from the chosen starting point.
      NrafterPruning = NrafterPruningSave[[PuncturedCoveringStartingPoint]]
      FilteringNeeded = FilteringNeededSave[[PuncturedCoveringStartingPoint]]
      NrRemoved =  NrRemovedSave[[PuncturedCoveringStartingPoint]]
      method = methodSave[[PuncturedCoveringStartingPoint]]
      #Starting with the codebook from the chosen starting point
      Codes = TempStoragePrunedResults[[PuncturedCoveringStartingPoint]]
      OutputCodes = Codes
      print(paste("Range scanned, Starting with a punctured version of v =",PuncturedCoveringStartingPoint, "with", NrafterPruning, "Codes"))
    }
    else {print("No Strategy selected, check the code");break}
    
    ##########################################
    ###Processing regardless of Starting option (Except Covering Range in which case pruning is already done)
    ##########################################
    if (PunctureCoveringRange == FALSE){
      length = nrow(table)  
      #Convert sets to binary if needed:
      if (CustomStartingFile == FALSE | exists("CustomStartisSetbased")){
        tCodes = ConvertSettoBinary(table)
      } else tCodes = as.matrix(table) #if starting set is already binary based.
      
      #Error check if loading file goes wrong or website contains no codes
      if (sum(tCodes) == 0){
        print("No codeset scraped")
      }
      
      #Check that the HW is correct and whether a 100% solution is possible.
      if (sum(tCodes) == length*k){ #Checks that the tCodes has the correct HW.
        
        #Check if parameters precisely match a n^2 HW4 Hamming Code or a Steiner Code, in which case it will automatically be 100% efficient. (All Hamming Codes are also Steiner Codes but they are historically quite cool so worth checking for)
        if(!is.na(sum(match(v, c(2, 4, 8, 16, 32, 64, 128, 256))) > 0) & HW == 4){print("It's Hamming Time (100% utilization can be achieved using Hamming Codebooks)")} 
        HW4Steiners = c(8,10,14,16,20,22,26,28,32,34,38,40,44,46,50,52,56,58,62,64,68,70,74,76,80,82,86,88,92,94,98,100)
        HW5Steiners = c(11,23,35,47)
        HW6Steiners = c(12,24,36,48)
        if(!is.na(sum(match(v, HW4Steiners)) > 0) & HW == 4){print("Barcode Length matches a Steiner System, 100% of theoretical maximum can be achieved.")} 
        if(!is.na(sum(match(v, (HW4Steiners-1))) > 0) & HW == 4){print("Barcode Length is exactly one below a Steiner System, 100% of theoretical maximum can be achieved.")} 
        if(!is.na(sum(match(v, HW5Steiners)) > 0) & HW == 5){print("Barcode Length matches a Steiner System, 100% of theoretical maximum can be achieved.")} 
        if(!is.na(sum(match(v, (HW5Steiners-1))) > 0) & HW == 5){print("Barcode Length is exactly one below a Steiner System, 100% of theoretical maximum can be achieved.")} 
        if(!is.na(sum(match(v, HW6Steiners)) > 0) & HW == 6){print("Barcode Length matches a Steiner System, 100% of theoretical maximum can be achieved.")} 
        if(!is.na(sum(match(v, (HW6Steiners-1))) > 0) & HW == 6){print("Barcode Length is exactly one below a Steiner System, 100% of theoretical maximum can be achieved.")} 
        
        print(paste("Starting Codebook loaded properly, initial code set size:",length, ", with parameters; n =",v ,",k =",k , ",t =",t))
        
        } else {print("Codeset has codes with the wrong Hamming Weight, doublecheck code")}
      
      Codes = tCodes
      
      ######################################
      ## Analyze starting codebook for minHD conflicts
      ######################################
      
      HD = EvaluateCodebookHD(Codes)
      Rowconflicts = rowSums(HD == 2) #HD for a fixed HW can only be even. with minHD4, the only invalid HD is 2.
      
      ######################################
      ## If no pruning needed (no minHD conflicts):
      ######################################
      
      if (sum(Rowconflicts) == 0){
        print(paste("No conflicts, yield is ", round(nrow(tCodes)/TheoreticalMax*100,1),"% of Theoretical Maximum",sep = ""))
        OutputCodes = Codes
        FilteringNeeded = "No"
        NrRemoved = "None"
      }
      
      ######################################
      ## If pruning needed due to conflicts:
      ######################################
      
      if (sum(Rowconflicts) > 0){
        
        print(paste(sum(Rowconflicts/2, na.rm=TRUE), " Conflicts detected, lowest initial yield is ", round((nrow(tCodes)-sum(Rowconflicts, na.rm=TRUE)/2)/TheoreticalMax*100,1),"% of Theoretical Maximum",sep = ""))
        
        PruningOutput = PruningToConformToMinHD(HD,Codes)
        NrRemoved = PruningOutput[[1]]
        NrAfterPruning = PruningOutput[[2]]
        OutputCodes = PruningOutput[[3]]
        Codes = OutputCodes
        
        print(paste(NrRemoved," conflicts removed, after pruning the yield is ", nrow(Codes)," equal to ", round(nrow(OutputCodes)/TheoreticalMax*100,1),"% of Theoretical Maximum",sep = ""))
        FilteringNeeded = "Yes"
      }
    } #End of evaluating and pruning
  } #End of FreshStart-check
  
  TimePostPruning = Sys.time()
  
  ######################################
  ## Check if Codebook can be improved:
  ######################################
  
  #If already at theoretical maximum, move to output, otherwise run main iterative set exchange loop.
  if ((nrow(Codes)/TheoreticalMax) == 1){
    codeset_set = ConvertBinarytoSet(Codes)
  } else{
    
    
    ######################################
    ## Main Iterative Set Exchange Loop
    ######################################
    
    StartingNrofCodes = nrow(Codes)
    
    ImprovedCodebook_output = IterativeSetExchangeLoop(v, k, t, Codes, FreshStart, maxIterations, dynamicMaxIterations, CandidateCutoff, TheoreticalMax)
    
    codeset_set =ImprovedCodebook_output[[1]]
    if(!is.na(ImprovedCodebook_output[[2]])){TimeFirst100 = ImprovedCodebook_output[[2]]}
    if(!is.na(ImprovedCodebook_output[[3]])){ImpTime = ImprovedCodebook_output[[3]]}
    IterationsUsed = ImprovedCodebook_output[[4]]
    #convert output to binary
    length = nrow(codeset_set)
    OutputCodes = ConvertSettoBinary(codeset_set)
    print(paste("Finished Scavenging, Final size is",nrow(OutputCodes), "which is",round(nrow(OutputCodes)/TheoreticalMax*100,1), "% of the theoretical max at",TheoreticalMax  ))
    
    addedCodes = nrow(codeset_set) - StartingNrofCodes
  }
  
  TimePostScavenging = Sys.time()
  
  TimeTotal = TimePostScavenging - StartTime
  if (exists("TimeFirst100")){TimeUntil100Iterations = TimeFirst100-StartTime}
  if(exists("ImpTime")){Timetolastimp = ImpTime - StartTime; Timefromlastimp = TimePostScavenging-ImpTime}
  
  ######################################
  ## Output final Codebook and metadata
  ######################################
  
  #Prepare filenames
  filenameprefix = paste(v,"Bit_HW",k,"_HD",MinHD,"_finalsize",nrow(OutputCodes), sep = "")
  if (FilenameOverride != FALSE){filenameprefix = FilenameOverride}
  
  filenameBinary = paste(filenameprefix,"Binary.csv", sep="")
  filenameSet = paste(filenameprefix,"Set.csv", sep="")
  metafilename = paste("meta_",filenameprefix,".txt")
  print(paste("Result files and metadata saved at:  ", Outputfolder))
  print(paste("      with filenames starting with:  ",filenameprefix))
  #If specific metadata do not exists, create them with "NA"
  if (!exists("method")){method = NA}
  if (!exists("FilteringNeeded")){FilteringNeeded = NA}
  if (!exists("NrAfterPruning")){NrAfterPruning = NA}
  if (!exists("NrRemoved")){NrRemoved = NA}
  if (!exists("addedCodes")){addedCodes = NA}
  if (!exists("IterationsUsed")){IterationsUsed = NA}
  if (!exists("TimeUntil100Iterations")){TimeUntil100Iterations = NA}
  if (!exists("Timetolastimp")){Timetolastimp = NA}
  if (!exists("Timefromlastimp")){Timefromlastimp = NA}
  if (!exists("TimeTotal")){TimeTotal = NA}
  if (!exists("PuncturedCoveringStartingPoint")){PuncturedCoveringStartingPoint = NA}
  
  metadata = list(
    "Barcode Length" = Bits, 
    "Hamming Weight" = HW, 
    "Minimum Hamming Distance" = MinHD, 
    "Theoretical Max (Johnson Bound)" = TheoreticalMax, 
    "StrategyUsed" = Strategy,
    "Final Codebook Size:"  = nrow(OutputCodes), 
    "Percentage Yield in %" = 100*(nrow(OutputCodes)/TheoreticalMax), 
    "If starting from a punctured covering design, which v was chosen" = PuncturedCoveringStartingPoint,
    "Starting Code from La Jolla Covering Repository created by:" = method, 
    "Pruning Needed" = FilteringNeeded, 
    "If Pruned: Nr of codes Removed" = NrRemoved,  
    "Codebook Size after pruning" = NrAfterPruning,
    "Codes added via iterative set exchange loop" = addedCodes, 
    "Max Nr of Iterations after last improvement:" = maxIterations, 
    "Total Nr of Iterations used by set exchange loop:" = IterationsUsed,
    "Timing: Total Time" = TimeTotal,
    "Timing: From Start to First 100 Iterations (For very complex parameters, this is a large percentage of the time" = TimeUntil100Iterations,
    "Timing: Time from Start until last improvement to the codebook" = Timetolastimp,
    "Timing: Time from last improvement until end (quantifies the cost of increasing the maxIterations parameter)" = Timefromlastimp)
  sink(metafilename)
  print(metadata)
  sink()
  
  write.table(OutputCodes,filenameBinary, row.names = FALSE, col.names = FALSE)
  if (exists("codeset_set")){write.table(codeset_set,filenameSet, row.names = FALSE, col.names = FALSE)}
  return(nrow(OutputCodes))
} 