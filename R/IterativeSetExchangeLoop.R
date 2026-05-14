IterativeSetExchangeLoop = function(v, k, t, Codes, FreshStart, maxIterations, dynamicMaxIterations, CandidateCutoff, TheoreticalMax){
  
  
  tsets = t(combn(1:v,t))
  All_ksets = t(combn(1:v,k))
  
  tsetstemp = tsets
  codeset_bin = Codes
  #FreshStart initializes with one 1:k Code as starting seed. A bit wonky if starting with a NA-row.
  if (FreshStart == TRUE){
    Codebook_Set = matrix(1:k,nrow=1)}
  else{
    Codebook_Set = ConvertBinarytoSet(codeset_bin)
  }  
  #OBS: First time Codebook_Set is created it is a matrix. Second round below will convert it to a tibble.
  
  #---------------------------------------#
  # Main Scavenging loop
  #---------------------------------------#
  
  IterationCounter = 0
  maxIterationsloop = maxIterations #maxIterationsloop can dynamically be increased during the running depending on the finding of new codes.
  if (FreshStart == TRUE){maxIterationsloop = TheoreticalMax+maxIterations} #as it needs extra time to build all the easy pickings first.
  
  while (TRUE){
    IterationCounter = IterationCounter +1
    IterationsUsed = IterationCounter
    if (IterationCounter == 100){TimeFirst100 = Sys.time()}   #As the first 100 iterations take more time, it is valuable to output how long time this took.
    if (maxIterationsloop <= IterationCounter){break}
    
    
    #Unlist Codebook_Set to a matrix. This is needed because it is the way it initially enters the loop and tibbles interfere with the first usages of it.
    Codebook_Set = matrix(unlist(Codebook_Set, use.names = FALSE), ncol = k)
    
    ############################################    
    #Generate a list of used t-sets
    ############################################
    nrow_cs = nrow(Codebook_Set)
    used_tsets = matrix(ncol = k-1, nrow = nrow_cs*k) 
    for (i in 1:k){   #A way to further generalize this part. Make (i in 1:choose(k,t)), then run through each option and subset by it. 
      submatrix = matrix(Codebook_Set[,(c(1:k)[-i])], nrow = nrow_cs)
      used_tsets[(i-1)*nrow_cs+1:nrow_cs,] =  submatrix
    }
    used_tsets = as.data.frame(used_tsets)
    used_tsets_withindex = cbind(used_tsets,0,rep(1:nrow(Codebook_Set),choose(k,t)))
    used_tsets_withindex = as.data.frame(used_tsets_withindex)
    
    ############################################    
    #Generate a list of unused t-sets and k-sets  
    ############################################    
    unused_tsets <- as.data.frame(rbind(tsets,used_tsets)) %>% group_by(across(everything())) %>% filter(n() ==1) 
    unused_ksets <- as.data.frame(rbind(All_ksets,Codebook_Set)) %>% group_by(across(everything())) %>% filter(n() ==1) 
    #Within the loop, Codebook_Set is added or subtracted to when needed.
    
    ############################################    
    #Generate ghost k-sets; comprising all potential k-sets from the list of unused t-sets. 
    ############################################     
    #First create every possible k-set. Then count how many times each was created. If k times = EasyPickings, if t times = Candidates.
    unused_tsets_df = as.data.frame(unused_tsets)
    unused_tsets_m = as.matrix(unused_tsets_df)
    nrow_uut = nrow(unused_tsets_df)
    
    
    ghost_ksets = matrix(as.integer(0),k,nrow_uut*v)
    ghost_ksets[1:t,] = matrix(rep(unused_tsets_m,each =v), nrow = t , byrow = TRUE )
    ghost_ksets[k,] = rep(1:v,nrow_uut)
    ghost_ksets = t(ghost_ksets)
    for (i in 1:t){
      ghost_ksets=ghost_ksets[ghost_ksets[,k] !=  ghost_ksets[,i],]
    }
    ghost_ksets= matrix(ghost_ksets[order(row(ghost_ksets), ghost_ksets)], ncol=ncol(ghost_ksets), byrow=TRUE)    
    
    ############################################    
    #Identify EasyPickings
    ############################################   
    
    EasyPickings = as.data.frame(ghost_ksets) %>% group_by(across(everything())) %>% filter(n() ==k) %>% distinct_all()
    
    if (nrow(EasyPickings)>0){
      #Add the EasyPicking to the codebook. Restart the loop to recalculate used/unused sets.
      Codebook_Set = rbind(as.data.frame(Codebook_Set),EasyPickings[sample(1:nrow(EasyPickings),1),])
      print(paste("Iteration",IterationCounter,"Adding Found EasyPicking: Codes +1, now", nrow(Codebook_Set), "unique codes" ))
      ImpTime = Sys.time() #Time of last improvement.
      next   
    }   
    
    ############################################    
    #Identify Candidates (ghost k-sets that needs one t-set from the used t-sets)
    ############################################     
    
    Candidates = as.data.frame(ghost_ksets) %>% group_by(across(everything())) %>% filter(n() ==(t)) %>% distinct_all()
    Candidates_m = as.matrix(Candidates)
    #Break the loop if too few Candidates.
    if (nrow(Candidates) < CandidateCutoff){IterationsUsed = IterationCounter; paste("Out of t-set candidates to continue");break}
    
    nrow_cand = nrow(Candidates)
    Candidate_tsets = matrix(0,ncol=k-1,nrow=nrow_cand*k)
    #Candidate_tsets = matrix(ncol = k-1, nrow = 0)
    for (i in 1:k){
      Candidate_tsets[(1:nrow_cand)+(i-1)*nrow_cand,] = Candidates_m[,(1:k)[-i]]
      #submatrix = as.matrix(Candidates[,(c(1:k)[-i])])
      #Candidate_tsets =  (rbind(Candidate_tsets,submatrix))
    }
    Candidate_tsets = as.data.frame(Candidate_tsets)
    Candidate_tsets$originCandidate = rep(1:nrow(Candidates),k)
    
    
    #Filter Candidate_tsets and find tsets from the used set.
    Candidate_tsets_withindex = cbind(Candidate_tsets[,], c(rep(0,nrow(Candidate_tsets))))
    Candidate_tsets_withindex_sliced = Candidate_tsets_withindex %>% group_by(across(all_of(c(1:t)))) %>% slice_sample(n = 1) %>% ungroup() #For random candidate choosing later on.
    
    #TODO: Non-crashing error message warning about ambiguity in across(c(1:t)), can potentially be done more robustly with across(all_of(c(1:t))).
    #See <https://tidyselect.r-lib.org/reference/faq-external-vector.html>.
    # group_by(across(c(1:t))) --> group_by(across(all_of(c(1:t))))
    
    
    #Some data wrangling to make the two data frames comparable
    combined = as.data.frame(rbind(used_tsets_withindex,as.matrix(setNames(Candidate_tsets_withindex, names(used_tsets_withindex)))))
    combinedclean = matrix(as.numeric(unlist(combined, use.names = FALSE)),nrow(combined),k+1)
    
    combined_sliced = as.data.frame(rbind(used_tsets_withindex,as.matrix(setNames(Candidate_tsets_withindex_sliced, names(used_tsets_withindex)))))
    combinedclean_sliced = matrix(as.numeric(unlist(combined_sliced, use.names = FALSE)),nrow(combined_sliced),k+1)
    
    Candidate_tsets_used =as.data.frame(combinedclean) %>% group_by(across(c(1:t))) %>% filter(n() >1) %>% distinct_all()   
    Candidate_tsets_used_sliced =as.data.frame(combinedclean_sliced) %>% group_by(across(c(1:t))) %>% filter(n() >1) %>% distinct_all()  
    
    # Checking networking between Candidates themselves (as two candidates who are conflicting with each other is not an useful addition)
    used_ksets_candidate_count =as.data.frame(combinedclean) %>% group_by(across(c(1:t))) %>% filter(n() >1) %>% summarise("MatchingCode" = max(across(paste("V",t+2,sep=""))), "NrofCandidates" = (n()-1), .groups = "drop") %>% filter(MatchingCode > 0)
    used_ksets_with_multiple_candidates = used_ksets_candidate_count %>% group_by(MatchingCode) %>% summarise("SumNrofCandidates" = sum(NrofCandidates)) %>% filter(SumNrofCandidates >1)
    
    #For every Main Code that has two or more Candidates, go through it and extract the Candidates it links to, then check if they are close together. 
    print(paste("Iteration",IterationCounter,"/",maxIterationsloop,".Scanning candidates. Nr of Candidates available = ", nrow(Candidates) ),sep="")
    FoundOne = FALSE
    nrow_multicand = nrow(used_ksets_with_multiple_candidates)
    if (nrow_multicand > 0){
      
      Candidate_tsets_usedtemp = Candidate_tsets_used
      Candidate_tsets_usedtemp$MainCode = 0    #OBS This has both maincode and Candidates plus 2 columns denoting origin.
      
      for (i in 1:nrow_multicand){
        
        codeIndex = as.numeric(used_ksets_with_multiple_candidates[i,1])
        Codetsets = cbind(as.data.frame(t(combn(Codebook_Set[codeIndex,],t))),matrix(0,choose(k,t),2))   
        names(Codetsets)[t+2]="MainCodeOrigin"
        names(Codetsets)[t+1]="CandidateOrigin"
        Codetsets$MainCode = 1
        Candidate_tsets_matchingMaincode = rbind(Codetsets, setNames(Candidate_tsets_usedtemp, names(Codetsets))) %>% mutate_at(c(1:t), as.numeric) %>% group_by(across(c(1:t))) %>% filter(any(MainCode == 1)) %>% ungroup() %>% filter(MainCode == 0) %>% filter(MainCodeOrigin == 0) %>% pull(t+1)
        
        #: subset candidates first, before the loop.
        nrow_MatchingCands = length(Candidate_tsets_matchingMaincode)
        Candidatesmatchingmaincode_m = Candidates_m[Candidate_tsets_matchingMaincode,]
        
        MinMatch = 100
        for (j in 1:(nrow_MatchingCands-1)){   
          a = Candidatesmatchingmaincode_m[j,]
          for (h in (j+1):nrow_MatchingCands){
            b = Candidatesmatchingmaincode_m[h,]
            MinMatcht = min(MinMatch,length(intersect(a,b)))
            #If MinMatch is the smallest so far, save j and h.
            if (MinMatcht < MinMatch){j_save = j; h_save=h }
            MinMatch = MinMatcht
          }}  
        
        #MinMatch is the max shared number between two k-sets. In order to not share a t-set, this needs to be smaller than t.
        
        if (MinMatch >= t){next} #Check next row in network 2 until network 2 is depleted. 
        else {  #Will only kick in once it finds a good pair of Candidates (low MinMatch) 
          #Kick out the MainCode we are currently at and add one of the Candidate pairs with the best fit.
          CodetoRemove = used_ksets_with_multiple_candidates[i,1]
          Codebook_Set = Codebook_Set[-unlist(CodetoRemove, use.names = FALSE),]
          AddCandidates = c(Candidate_tsets_matchingMaincode[j_save], Candidate_tsets_matchingMaincode[h_save])
          Codebook_Set = rbind(as.data.frame(Codebook_Set),Candidates[AddCandidates,])
          print(paste("Found Double compatible Candidates.                         Code Set Size = ",nrow(Codebook_Set) ))
          ImpTime = Sys.time()
          
          if (dynamicMaxIterations == TRUE){maxIterationsloop = max(maxIterationsloop, IterationCounter+maxIterations); print(paste("Iterations remaining increased by",maxIterations))}
          FoundOne = TRUE; break #Need to kick out of the used_ksets_with_multiple_candidates-loop using FoundOne=TRUE as a tag in order to be properly kicked out of the main loop without doing random candidate stuff. Kinda like the kicks in inception...
        }
      }}
    
    if (FoundOne == TRUE){next} #Making sure to restart if it just did the replacement above.
    else{  
      #Choose a random candidate to knock into the codeset
      CandidateRandomizer =as.data.frame(combinedclean_sliced) %>% group_by(across(c(1:t))) %>% filter(n() >1) %>% summarise("MatchingCode" = max(across(paste("V",t+2,sep=""))), "NrofCandidates" = (n()-1), "RandomCandidate" = max(across(paste("V",t+1,sep=""))), .groups = "drop") %>% filter(MatchingCode > 0)
      RandomCandidateIndex = sample(1:nrow(CandidateRandomizer),1) 
      RandomCandidate = CandidateRandomizer[RandomCandidateIndex,t+3] %>% pull(1)
      RandomCode = CandidateRandomizer[RandomCandidateIndex,t+1] %>% pull(1)
      ##As the numbers of codes will be the same, the new code is inserted in the same spot as the old code, which avoids rbind and saves computational time
      Codebook_Set[as.integer(RandomCode),] = Candidates[as.integer(RandomCandidate),]
      next
    }
  }
  Codebook_Set = matrix(unlist(Codebook_Set, use.names = FALSE), ncol = k)
  if (!exists("ImpTime")){ImpTime = NA}
  if (!exists("TimeFirst100")){TimeFirst100 = NA}
  output=list(Codebook_Set,TimeFirst100, ImpTime, IterationsUsed)
  return(output)
}