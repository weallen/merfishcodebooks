#Simulator Code
CodeFolder = "C:\\Users\\Adameyko\\Desktop\\HammingCode batch runs\\RCodeLibrary"
OutputFolder = "C:\\Users\\Adameyko\\Desktop\\HammingCode batch runs\\SimulatorOutput"
GeneExpressions = #csv-file with columns corresponding to different cell types or experiments.
Codebook_input = #A codebook in binary format that genes are assigned to  
library(ggplot2)
library(dplyr)
setwd(CodeFolder)
source("ConvertBinarytoSet.R")


##################################
###Assumptions about Detectability
##################################
#Assumptions are made without using expansion microscopy.

## Diffraction Limit, using GFP
WaveLength= 0.5 #micrometers
NumAperture = 1.4
DiffractionLimit = WaveLength/(2*NumAperture) #micrometers

CellWidth = 100 #micrometers
CellArea = CellWidth^2

MinDist = DiffractionLimit 

##################################
###Assumptions about Expression levels
##################################

##Full transcriptome reads per cell
DetectableTranscriptsPerCell = 1e5
# From Xia et al, PNAS 2019, targeting ~10 000 genes in U2OS cells:  "92,000 ± 32,000 (mean ± SD) transcripts per cell"
# Expansion Microscopy was utilized in this paper, so we only grab the approximate detectable limit from it.


#For the examples in the manuscript, we used a column of average expressions from a sensory neuron population to simulate gene expressions. Other sources can replace it below.
#Load gene averages
setwd(OutputFolder)
ClusterAverages=read.csv(GeneExpressions)
SensoryNeuronAverages=ClusterAverages$Sensory
SensoryNeuronProp = SensoryNeuronAverages/sum(SensoryNeuronAverages)
SensoryNeurons100k = round(DetectableTranscriptsPerCell*SensoryNeuronProp)
sum(SensoryNeurons100k)
NrofGenes = nrow(ClusterAverages)
mRNAs = as.data.frame(cbind(1:sum(SensoryNeurons100k)),0,0)
mRNAs$coords_x = runif(sum(SensoryNeurons100k))*CellWidth #micrometers
mRNAs$coords_y = runif(sum(SensoryNeurons100k))*CellWidth #micrometers
mRNAs$Gene = "ToAdd"
mRNAs$Conflict = "FALSE"
mRNAs$ID = 1:nrow(mRNAs)
i = 0
row = 1
while (TRUE){
  i = i+1
  if (i > NrofGenes){break}
  
  NrtoAdd = SensoryNeurons100k[i]
  if (NrtoAdd>0){
    mRNAs$Gene[row:(row+NrtoAdd-1)]=ClusterAverages[i,1]
    row = row+NrtoAdd
  }
}

library(ggplot2)
ggplot(mRNAs[,], aes(x=coords_x, y = coords_y, color = Gene)) + geom_point(show.legend=FALSE, alpha = 0.5) + theme_bw()


#Simulate different MERFISH environments and mark conflicts

#Randomize a set of genes that are present in the transcript simulation.
transcriptsNames = sample(unique(mRNAs$Gene),1000)
transcripts = mRNAs[mRNAs$Gene %in% transcriptsNames,]
transcriptsExpr = ClusterAverages[ClusterAverages$X %in% transcriptsNames,"Sensory"]
transcriptsNames_order = ClusterAverages[ClusterAverages$X %in% transcriptsNames,"X"]

transcriptsExpr = as.data.frame(cbind(transcriptsExpr,transcriptsNames_order))
colnames(transcriptsExpr) = c("AvgExpr","Gene")
transcriptsExpr$AvgExpr = as.numeric(transcriptsExpr$AvgExpr)

transcriptsExpr = as.data.frame(transcriptsExpr) %>% arrange(-AvgExpr)
transcriptsNames = transcriptsExpr$Gene

##Gene Assignment to Codebook
Codebook = read.csv(Codebook_input,sep=" ", header=FALSE)
HW=4
nrow(Codebook)
Codebook_Codebook = cbind(c(transcriptsNames,rep("blank",nrow(Codebook)-length(transcriptsNames))), Codebook)
colnames(Codebook_Codebook)[1] = "Gene"
transcripts_joined = left_join(transcripts,Codebook_Codebook, by = join_by(Gene == Gene))


for (i in 1:nrow(transcripts_joined)){
  CurrentmRNA = transcripts_joined[i,]
  ID = CurrentmRNA$ID
  Probes = CurrentmRNA[,7:(7+HW-1)]
  xpos = CurrentmRNA$coords_x
  ypos = CurrentmRNA$coords_y
  mRNAsinvicinity = transcripts_joined[transcripts_joined$coords_x>=xpos-MinDist & transcripts_joined$coords_x<xpos+MinDist & transcripts_joined$coords_y>=ypos-MinDist & transcripts_joined$coords_y<ypos+MinDist   ,]
  if (nrow(mRNAsinvicinity)>1){
    mRNAsinvicinity = mRNAsinvicinity[mRNAsinvicinity$ID!=ID,]
    ConflictDetected = colSums(apply(mRNAsinvicinity[,7:(7+HW-1)], 1, function(x) Probes %in% x)) >0
    Conflict_indexes = mRNAsinvicinity$ID[ConflictDetected]
    
    if (length(Conflict_indexes)>=1){
      transcripts_joined$Conflict[transcripts_joined$ID == ID]=TRUE
      transcripts_joined$Conflict[transcripts_joined$ID %in% as.numeric(Conflict_indexes)]=TRUE
      
    }}
  print(paste("Row ",i," is done"))
}

CodebookORDEREDsave = transcripts_joined
Codebooksave = transcripts_joined

ggplot(Codebooksave, aes(x=coords_x, y = coords_y, color = Conflict)) + geom_point(show.legend=FALSE) + theme_bw() + scale_color_manual(values = c("darkblue","red"))
sum(as.logical(Codebooksave$Conflict))/nrow(Codebooksave)