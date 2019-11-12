import time
#import winsound
import random
class standard_XCS_config:
    def __init__(self):
        self.XCS_version='45598a9f_15e3_4393_b4e4_da00bc199dfd'
        #XCS configure parameters
        self.alpha=0.1 #The fall of rate in the fitness evaluation.

        self.beta=0.2 # The learning rate for updating fitness, prediction, prediction error, and action set size estimate in XCS's classifiers.

        self.gama=0.95 # The discount raye in multi-step problems

        self.delta=0.1 #The fraction of the mean fitness of the population below which the fitness of a classifier may be considered in its vote for deletion.

        self.nu=5.0 #Specifies the exponent in the power function for the fitness evaluation

        self.theta_GA=25.0#The threshold for the GA application in an action set.

        self.epsilon_0=10.0#The error threshold under which the accuracy of a classifier is set to one.

        self.theta_del=20#Specified the threshold over which the fitness of a classifier may be considered in its deletion probability.

        self.pX=0.8#The probability of mutating one allele and the action in an offspring classifier

        self.crossoverType=2 #0 uniform, 1 onePoint, and 2 twopoint crossover.

        self.pM=0.04 # The probability of mutating one allele and the action in an offerspring classifier.

        self.mutationType =0 #0 niche and 1 general mutation

        self.P_dontcare =0.5 #The probability of using a don't care symbol in an allele when covering

        self.predictionErrorReduction=1.0#0.25 The reduction of the prediction error when generating an offspring classifier.

        self.fitnessReduction=0.1 #The reduction of the fitness when generating an offspring classifier.

        self.theta_sub=20 # The experience of a classifier required to be a subsumer

        self.predictionIni=10.0 #The initial prediction value when geneerating a new classifier (e.g in covering).

        self.predictionErrorIni=0.0 #The initial prediction error value when generating a new classifier (e.g in cvering)

        self.fitnessIni=0.01 # The initial fitness value when generating a new classifier (e.g in covering)

        self.doGASubsumption =True # specifies if GA subsumption should be executed.

        self.doActSetSubsumption =False #True specifies if action set subsumption should be executed

        self.tournametSize =0.4 #The fraction of classifiers participating in a tournament from an action set.

        self.forceDifferentInTournament=0.0

        self.doGAErrorBasedSelect=False

        self.selecTolerance=0.05

        self.dontcare='#' #The don't care symbol (normally '#')

        # for training
        self.maxPayOff=1000
        
        self.numActions=2#The number of actions

        #problem set config
        self.execute_number=0
        self.maxPopSize=4000
        self.maxproblemsize=10000
        self.condition_length=20   #  the length of the condition
        self.dont_care_probability=0.33# the propability for generate the don't care symbol
        self.posBits =4 # for multiplexer problem 11bit posbit=3, 6 bit posbit=2
        self.numRelevantBits = 2# for hidden problems
        self.posRelevantBits = [0,1] # for hidden problems

        #   DV1 problem settings
        self.DV1 = [1, 2, 3, 8, 9, 10, 11, 13, 14, 24, 25, 26, 27, 28, 30, 40, 41, 42, 43, 46, 47, 56, 57, 58, 59, 61, 65, 66, 67, 69, 70, 71, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 88, 89, 90, 91, 93, 94, 95, 97, 98, 99, 101, 102, 103, 104, 105, 106, 107, 109, 110, 113, 114, 115, 117, 118, 121, 122, 123, 125, 126, 127]
        self.sizeDV1 = 74

        #folder Address
        self.savefolder='XCS_Result.txt'

    def startTimer(self):
        local_time= time.localtime(time.time())
        format_time=time.strftime('DAY: %Y-%m-%d  Time: %H : %M : %S',local_time)
        #print format_time
        #print local_time
        Hour= local_time[3]
        Min= local_time[4]
        second= local_time[5]
        return format_time,Hour,Min,second

    def elapsed(self,Hour1,Hour2,Min1,Min2,second1,second2):
        result=0
        result=result+second1-second2
        result=result+60*(Min1-Min2)
        result=result+3600*(Hour1-Hour2)
        return result

    def finish(self):
        winsound.Beep(600,1000)

class XCSCFC_config:
    def __init__(self):
        self.numAction=2#0 or 1
        self.posBit=3#2,3,4,5,6,and 7 for 6-, 11-, 20-,37-,70- and 135-bits MUX problem respectively
        self.condLength=11#posBits+pow(2,posBits)
        self.maxPopSize=50*1000#specifies the maximal number of micro-classifiers in the population (0.5,1,2,5,10/20,50)*1000 for  6-,11-,20-,37-,60-,135-bit MUX respecitively
        self.maxProblems=50*100*1000#training set=(5,5,5,5/10,20,50)*100*1000 for 6-, 11-, 20-, 37-, 70-, 135- bits MUX respectively
        self.maxPayoff=1000

        self.currentProblemLevel= self.posBit-1
        self.clfrCondLength=self.condLength/4 #conditionlength/2 and conditionlength/4 for 70mux and 135mux respectively

        self.cfMaxDepth=2
        self.cfMinDepth=0
        self.cfMaxLength=8#pow (2,adfMaxDepth+1) allow for endstop OPNOP
        self.cfMaxArity=2
        self.cfMaxStack=(self.cfMaxArity-1)*(self.cfMaxDepth-1)+2

        self.OPNOP=-100
        self.OPAND=-101
        self.OPOR=-102
        self.OPNAND=-103
        self.OPNOR=-104
        self.OPNOT=-105

        self.OPNOP_str='o'
        self.OPAND_str='&'
        self.OPOR_str='|'
        self.OPNAND_str='d'
        self.OPNOR_str='r'
        self.OPNOT_str='~'

        self.totalFunctions=5
        self.functionCodes=[self.OPAND,self.OPOR,self.OPNAND,self.OPNOR,self.OPNOT]

        self.alpha=0.1 # the fall of rate in the fitness evaluation
        self.beta=0.2 # the learning rate for updating fitness, prediction, prediction error, and action set size estimate in the XCS's classifiers.
        self.gama=0.95 #The discount rate in multi-step problems
        self.delta=0.1 #The fraction of the mean fitness of the population below which the fitness of a classifier may be considered in its vote for deletion.
        self.nu=5.0#specifies the exponent in the power function for the fitness evaluation
        self.theta_GA=25.0#The threshold for the GA application in the action set
        self.epsilon_0=10.0#The error threshold under which the accuracy of a classifier is set to one
        self.theta_del=20#Specified the threshold over which the fitness of a classifier may be considered in its deletion probability.
        self.pX=0.8#The probability of applying crossover in an offspring classifier
        self.crossoverType=2#0 uniform, 1 onePoint, and 2 twoPoint crossover.
        self.pM=0.04#The probability of mutating one allel and the action in an offspring classifier
        self.mutationType=0#//0 niche, and 1 general mutation
        self.P_dontcare=0.33#The probability of using a don't care symbol in an allele when covering.
        self.pCF=0.5#The probability of a terminal to be a previous level code fragment
        self.predictionErrorReduction =0.25#The reduction of the prediction error when generating an offspring classifier.
        self.fitnessReduction=0.1#The reduction of the fitness when generating an offspring classifier.
        self.theta_sub=20 #The experience of a classifier required to be a subsumer
        self.predictionIni=10.0#The initial prediction value when generating a new classifier (e.g in covering)
        self.predictionErrorIni=0.0#The initial prediction error value when generating a new classifier
        self.fitnessIni=0.01#The initial prediction value when generating a new classifier
        self.doGAsubsumption=True#specifies if GA subsumption should be executed
        self.doActSetSubsumption=True#specified if action set subsumption should be executed.
        self.tournamentSize=0.4#The fraction of classifiers participating in a tournament from an action set.
        self.forceDifferentInTournament=0.0
        self.doGAErrorBasedSelection=False
        self.selectTolerance=0.0
        self.currentInstanceBasedAction=False
        self.P_dontcare='#'#The don't care symbol (normally '#')

    def startTimer(self):
        local_time= time.localtime(time.time())
        format_time=time.strftime('DAY: %Y-%m-%d  Time: %H : %M : %S',local_time)
        #print format_time
        #print local_time
        Hour= local_time[3]
        Min= local_time[4]
        second= local_time[5]
        return format_time,Hour,Min,second

    def elapsed(self,Hour1,Hour2,Min1,Min2,second1,second2):
        result=0
        result=result+second1-second2
        result=result+60*(Min1-Min2)
        result=result+3600*(Hour1-Hour2)
        return result

    def drand(self):
        result=random.random()
        return result

    #python version same as irand_old()
    def irand(self,n):
        result=random.randint(0,n-1)
        return result

   