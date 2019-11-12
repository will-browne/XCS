import random
import uuid
import time
import copy
from Config import standard_XCS_config
from Environment import environment


class standard_XCS:
    def __init__(self):
        self.config=standard_XCS_config()
        self.env=environment()
        self.savefolder='XCS_Result.txt'
        self.population={}
        self.match_set=[]
        self.action_set=[]

    ################ Create classifiers ##################
    #condition: state from environment
    #action: 0 or 1
    #setsize: action set size
    #time: the time use 
    def Create_Init_Classifier(self,condition,action,setsize,time):
        uuid_key=uuid.uuid1()
        classifier={'condition':condition,
                    'action':action,
                    'prediction':self.config.predictionIni,
                    'predictionError':self.config.predictionErrorIni,
                    'accuracy':self.config.fitnessIni,
                    'fitness':self.config.fitnessIni,
                    'numerosity':1,
                    'experience':0.0,
                    'actionSetSize':setsize,
                    'timeStamp':time,                   
                    }
        self.population.setdefault(uuid_key,classifier)
        return uuid_key


    def addtwodimdict(self,key_a,key_b,val):
        if key_a in self.population:
            self.population[key_a].update({key_b:val})
        else:
            self.population.update({key_a:{key_b:val}})

    ############### Create Match set ####################

    #Judge whether state match the condition in classifier if match return true otherwise return false
    def isConditionMatched(self,condition,state):
        for i in range(0,len(condition)):
            if condition[i]!=self.config.dontcare and condition[i] != state[i]:
                return False
        return True

    #Returns the number of actions in the set and returns which action is covered
    def nrActionsInSet(self):
        nr=0
        coveredActions=[]
        for i in range(0,self.config.numActions):
            coveredActions.append(False)
        #print coveredActions
        for cl in self.match_set:
            if nr<self.config.numActions:
                if coveredActions[self.population[cl]['action']]==False:
                    coveredActions[self.population[cl]['action']]=True
                    nr=nr+1
            else:
                 return nr,coveredActions
        return nr,coveredActions

    #create a condition which can match the input state
    def createMatchingCondition(self,state):
        condition=[0]*len(state)
        for i in range(0,len(state)):
            if(random.random()<self.config.P_dontcare):
                condition[i]=self.config.dontcare
            else:
                condition[i]=state[i]
        return condition


    #build a classifier which match the input instance
    def matchingCondAndSpecifiedAct(self,state,action,setSize,time):       
        condition=self.createMatchingCondition(state)
        uuid_key=self.Create_Init_Classifier(condition,action,setSize,time)
        self.match_set.append(uuid_key)

    
    # Gets the match-set that matches state from pop.
    # If a classifier was deleted, record its address in killset to be
    # able to update former actionsets.
    # The iteration time 'itTime' is used when creating a new classifier
    # due to covering. Covering occurs when not all possible actions are
    # present in the match set. Thus, it is made sure that all actions
    # are present in the match set.
    def getMatchSet(self,state,itTime):
        popSize=0
        setSize=0
        #print "begin"
        for i in self.population:
            #calculate the population size
            popSize=popSize+self.population[i]['numerosity']
            if(self.isConditionMatched(self.population[i]['condition'],state)):
                #add matching classifier to the matchset
                self.match_set.append(i)
                #calculate size of the match set
                setSize=setSize+self.population[i]['numerosity']

        representedActions,coveredActions=self.nrActionsInSet()
        #print representedActions,coveredActions

        # create covering classifiers, if not all actions are covered
        while (representedActions<self.config.numActions):

            #print popSize,self.maxPopSize
            #time.sleep(10)
            #make sure that all actions are covered
            for i in range(0,self.config.numActions):
                if coveredActions[i]==False:
                    self.matchingCondAndSpecifiedAct(state,i,setSize+1,itTime)
                    setSize=setSize+1
                    popSize=popSize+1

            # Delete classifier if population is too big and record it in killset
            while (popSize>self.config.maxPopSize):
                #print popSize,self.maxPopSize
                #time.sleep(5)
                #print popSize
                #print self.maxPopSize
                self.deleteStochClassifier_match_set()
                popSize=popSize-1
            representedActions,coveredActions=self.nrActionsInSet()

        #print representedActions,coveredActions

    ############################## deletion ############################################
    # Deletes one classifier in the population.
    # The classifier that will be deleted is chosen by roulette wheel selection
    # considering the deletion vote. Returns the operated classifier set and the location of the macro-classifier which got decreased by one micro-classifier.
    ####################### match set operations ##########################################    
        
    #return the vote for deletion of the classifier
    def getDelProp(self,uuid_number, meanFitness):
        average_fitness=1.0*self.population[uuid_number]['fitness']/self.population[uuid_number]['numerosity']
        #print average_fitness
        if average_fitness>=self.config.delta*meanFitness or self.population[uuid_number]['experience']<self.config.theta_del:
            result= 1.0*self.population[uuid_number]['actionSetSize']*self.population[uuid_number]['numerosity']
            return result
        else:
            result= 1.0*self.population[uuid_number]['actionSetSize']*self.population[uuid_number]['numerosity']*meanFitness/average_fitness            
            return result

    #Delete the marked classifier from the classifier set and match set
    def deleteTypeofClassifier_match_set(self,uuid_number):
        if self.population[uuid_number]['numerosity']>1:
            self.population[uuid_number]['numerosity']=self.population[uuid_number]['numerosity']-1
        else:
            del self.population[uuid_number]
            for i in range(0,len(self.match_set)):
                if uuid_number==self.match_set[i]:
                    #self.match_set.pop(i)
                    self.match_set.remove(uuid_number)
                    return

    def deleteStochClassifier_match_set(self):
        locations=[]
        location=0
        sum=0.0
        choicep=0.0
        meanf=0.0
        size=0
        #get the sum of the fitness and the numerosity
        for i in self.population:
            meanf=meanf+self.population[i]['fitness']
            size=size+self.population[i]['numerosity']
            locations.append(i)
        meanf=1.0*meanf/size

        #get the delete proportion, which depends on the average fitness
        for i in range(0,len(locations)):
            sum=sum+self.getDelProp(locations[i],meanf)

        #choose the classifier that will be deleted
        choicep=random.random()*sum

        #look for the classifier that will be deleted
        sum=self.getDelProp(locations[0],meanf)
        while sum<choicep:
            location=location+1
            sum=sum+self.getDelProp(locations[location],meanf)

        #print 'location',location
        #print 'sum',sum
        #print 'choicep',choicep
        #print 'meanf',meanf
        #print 'size',size
        #return result, location
        self.deleteTypeofClassifier_match_set(locations[location])


    ######################### prediction array operations ############################################
    #determines the prediction array out of the match set (match set should never be None)
    def getPredictionArray(self):
        predictionArray=[]
        sumClfrFitnessInPredictionArray=[]
        for i in range(0,self.config.numActions):
            predictionArray.append(0.0)
            sumClfrFitnessInPredictionArray.append(0.0)

        for i in self.match_set:
            predictionArray[int(self.population[i]['action'])]= predictionArray[int(self.population[i]['action'])]+self.population[i]['prediction']* self.population[i]['fitness']
            sumClfrFitnessInPredictionArray[int(self.population[i]['action'])]=sumClfrFitnessInPredictionArray[int(self.population[i]['action'])]+self.population[i]['fitness']

        for i in range(0,self.config.numActions):
            if sumClfrFitnessInPredictionArray[i]!=0:
                predictionArray[i]=predictionArray[i]/sumClfrFitnessInPredictionArray[i]
            else:
                predictionArray[i]=0
        return predictionArray,sumClfrFitnessInPredictionArray

    #selects an action randomly. The function assures that chosen action is represented by at least one classifier in the prediction array        
    def randomActionWinner(self,sumClfrFitnessInPredictionArray):
        ret=0
        ret=random.randint(0,self.config.numActions-1)
        while sumClfrFitnessInPredictionArray[ret]==0:
            ret=random.randint(0,self.config.numActions-1)
        return ret


    ######################## action set operations #########################################
    #constructs an action set out of the match set ms
    def getActionSet(self,action):
        for i in self.match_set:
            if action== self.population[i]['action']:
                self.action_set.append(i)
        

    # Updates all parameters in the action set.
    # Essentially, reinforcement Learning as well as the fitness evaluation takes place in this set.
    # Moreover, the prediction error and the action set size estimate is updated. Also,
    # action set subsumption takes place if selected. As in the algorithmic description, the fitness is updated
    # after prediction and prediction error. However, in order to be more conservative the prediction error is
    # updated before the prediction.
    # @param maxPrediction The maximum prediction value in the successive prediction array (should be set to zero in single step environments).
    # @param reward The actual resulting reward after the execution of an action.
    def updateActionSet(self,max_prediction,reward):

        P=0.0
        setsize=0.0
        P=reward+self.config.gama*max_prediction


        for i in self.action_set:
            setsize= setsize+self.population[i]['numerosity']
            self.population[i]['experience']=self.population[i]['experience']+1

        #(important)update prediction, prediction error and action set size estimate
        for i in self.action_set:
            #first adjustments: simply calculate the average
            if self.population[i]['experience']<(1.0/self.config.beta):
                self.population[i]['predictionError']=(self.population[i]['predictionError']*(float(self.population[i]['experience'])-1.0)+abs(P-self.population[i]['prediction']))/float(self.population[i]['experience'])
                #print "predictionError",classifier_set[i].predictionError
                self.population[i]['prediction']=((self.population[i]['prediction']*(float(self.population[i]['experience'])-1.0))+P)/float(self.population[i]['experience'])
                #print "prediction",classifier_set[i].prediction
                self.population[i]['actionSetSize']=((self.population[i]['actionSetSize'] * (float(self.population[i]['experience'])-1.0))+setsize)/float(self.population[i]['experience'])
                #print "actionSetSize",classifier_set[i].actionSetSize
            #normal adjustment: use widrow hoff delta rule
            else:
                self.population[i]['predictionError']=self.population[i]['predictionError']+self.config.beta*(abs(P-self.population[i]['prediction'])-self.population[i]['predictionError'])
                #print "predictionError",classifier_set[i].predictionError
                self.population[i]['prediction']=self.population[i]['prediction']+self.config.beta*(P-self.population[i]['prediction'])
                #print "prediction",classifier_set[i].prediction
                self.population[i]['actionSetSize']=self.population[i]['actionSetSize']+self.config.beta*(setsize-self.population[i]['actionSetSize'])
                #print "actionSetSize",classifier_set[i].actionSetSize

        self.updateFitness()


        if(self.config.doActSetSubsumption):
            self.doActionSetSubsumption()



    #update the fitnesses of an action set (the previous[A] in multi-step envs or the current [A] in single-step envs
    def updateFitness(self):
        ksum=0.0
        #if the action set got NULL (due to deletion) return
        if len(self.action_set)==0:
            return 

        #First, calculate the accuracies of the classifier and the accuracy sums
        for i in self.action_set:
            if self.population[i]['predictionError']<=self.config.epsilon_0:
                self.population[i]['accuracy']=1.0
            else:
                if self.population[i]['prediction']==0.0:
                    self.population[i]['accuracy']==0
                else:
                    self.population[i]['accuracy']=self.config.alpha*pow( self.population[i]['prediction']/self.config.epsilon_0,-(self.config.nu))

            ksum=ksum+self.population[i]['accuracy']*float(self.population[i]['numerosity'])

        #Next, update the fitnesses accordingly
        for i in self.action_set:
            if ksum==0:
                self.population[i]['fitness']=self.population[i]['fitness']+self.config.beta*(-self.population[i]['fitness'])
            else:
                self.population[i]['fitness']=self.population[i]['fitness']+self.config.beta*((self.population[i]['accuracy']*self.population[i]['numerosity'])/ksum-self.population[i]['fitness'])



    ################################ subsumption deletion #################################
    #Check if the first condition is more general than the second.
    #It is made sure that the classifier is indeed more general and not equally general
    #as well as that the more specific classifier is completely included in the more general one (do not specify overlapping regions).
    def isMoreGeneral(self,first_condition,second_condition):
        answer=False
        for i in range(0,len(first_condition)):
            if first_condition[i]!=self.config.dontcare and first_condition[i] !=second_condition[i]:
                return False
            elif first_condition[i]!=second_condition[i]:
                answer=True
        return answer

    def isSubsumer(self,uuid):
        result= int(self.population[uuid]['experience'])>self.config.theta_sub and self.population[uuid]['predictionError']<=self.config.epsilon_0
        return result

    def doActionSetSubsumption(self):

        subsumer=None
        #find the most general subsumer
        for i in self.action_set:            
            if(self.isSubsumer(i)):
                if(subsumer==None):
                    subsumer=i
                elif(self.isMoreGeneral(self.population[i]['condition'],self.population[subsumer]['condition'])):
                     subsumer=i
        
        #If a subsumer was found, subsume all classifiers that are more specific
        if subsumer!= None:
            for i in self.action_set:
                if i != subsumer:
                    if(self.isMoreGeneral(self.population[subsumer]['condition'],self.population[i]['condition'])):
                        self.population[subsumer]['numerosity']=self.population[subsumer]['numerosity']+self.population[i]['numerosity']
                        del self.population[i]

    ############################ discovery mechanism #########################################
    #selects a classifier from 'set' using tourment selection
    #If 'notMe' is not the Null and forceDifferentInTournament is set to a value larger 0,
    # this classifier is not selected except if it is the only classifier.
    def selectClassifierUsingTournamentSelection(self):
        winnerSet=[]
        fitness=-1.0

        #there must be at least one classifier in the set
        #if classifierset==None or len(classifierset)==0:
        #    print "in selectClassifierUsingTournamentSelection classifierset mustn't be None"
        

        #only one classifier in set
        if len(self.action_set)==1:
            return self.action_set[0]

        #tournament with fixed size
        #tournament selection with the tournament size approx. equal to tournamentSize setsum
        while len(winnerSet)==0: 
            for i in self.action_set:
                #if his fitness is worse then do not bother
                if len(winnerSet)==0 or  (fitness-self.config.selecTolerance) <= (self.population[i]['fitness']/self.population[i]['numerosity']):
                    for j in range(0,self.population[i]['numerosity']):
                        if random.random()<self.config.tournametSize:
                            if len(winnerSet)==0:
                                #the first one
                                winnerSet.append(i)
                                fitness=self.population[i]['fitness']/self.population[i]['numerosity']

                            else:
                                if (fitness+self.config.selecTolerance) > (self.population[i]['fitness']/self.population[i]['numerosity']) :
                                    winnerSet.append(i)

                                else:
                                    winnerSet=[]
                                    winnerSet.append(i)
                                    fitness=self.population[i]['fitness']/self.population[i]['numerosity']
                            break

        #print winnerSet
        if len(winnerSet)>1:
            size=random.randint(0,len(winnerSet)-1)
            return winnerSet[size]
        return winnerSet[0]    
    
    #select two classifiers using chosen selection mechanism and copy them as offspring
    def selectTwoClassifiers(self):
        parents=[]
        offspring=[]
        for i in range(0,2):
            parent_ID=self.selectClassifierUsingTournamentSelection()
            parents.append(parent_ID)

            offspring_ID=self.Create_Init_Classifier(copy.deepcopy(self.population[parent_ID]['condition']),self.population[parent_ID]['action'],self.population[parent_ID]['actionSetSize'],self.population[parent_ID]['timeStamp'])
            self.population[offspring_ID]['prediction']=self.population[parent_ID]['prediction']
            self.population[offspring_ID]['predictionError']=self.population[parent_ID]['predictionError']
            self.population[offspring_ID]['accuracy']=self.population[parent_ID]['accuracy']
            self.population[offspring_ID]['fitness']=self.population[parent_ID]['fitness']/float(self.population[parent_ID]['numerosity'])
            offspring.append(offspring_ID)
        return parents, offspring                

    #calculate all necessary sums in the set for the discovery component
    def getDiscoversSums(self):
        fitsum=0.0
        setsum=0
        gaitsum=0
        for i in self.action_set:
            fitsum=fitsum+self.population[i]['fitness']
            setsum=setsum+self.population[i]['numerosity']
            gaitsum=gaitsum+self.population[i]['timeStamp']*self.population[i]['numerosity']
        return fitsum, setsum, gaitsum

    #crosse the two received classifiers using two-point crossove.
    def twoPointCrossover(self,offsprings):
        sep_1 = random.randint(0,len(self.population[offsprings[0]]['condition'])-1)
        sep_2 = random.randint(0,len(self.population[offsprings[0]]['condition'])-1)
        #print sep_1
        #print sep_2
        if sep_1>sep_2:
            help=sep_1
            sep_1=sep_2
            sep_2=help

        for i in range(sep_1,sep_2+1):
            help=self.population[offsprings[0]]['condition'][i]
            #print help
            self.population[offsprings[0]]['condition'][i]=self.population[offsprings[1]]['condition'][i]
            self.population[offsprings[1]]['condition'][i]=help

    #determines if crossover is applied and calls  then the selected crossover type
    def crossover(self,offsprings):
        if random.random()<self.config.pX:
            self.twoPointCrossover(offsprings)

    #Mutates the condition of the classifier. If one allele is mutated depends on the constant pM
    #This mutation is a niche mutation. It assures that the resulting classifier still matches the current situation
    def applyNicheMutation(self,offspring,state):
        for i in range(0, len(state)):
            if random.random()<self.config.pM:
                if self.population[offspring]['condition'][i]==self.config.dontcare:
                    self.population[offspring]['condition'][i]=state[i]
                else:
                    self.population[offspring]['condition'][i]=self.config.dontcare

    #Mutates the action of the classifier
    def mutateAction(self,offspring):
        use_action=self.population[offspring]['action']
        if random.random()<self.config.pM:
            while use_action==self.population[offspring]['action']:
                self.population[offspring]['action']=random.randint(0,self.config.numActions-1)

    def mutation(self,offspring,state):
        self.applyNicheMutation(offspring,state)
        self.mutateAction(offspring)


    #check if classifier cl1 subsumes cl2
    def subsumes(self,parent,offspring):
        result= self.population[parent]['action']==self.population[offspring]['action'] and self.isSubsumer(parent) and self.isMoreGeneral(self.population[parent]['condition'],self.population[offspring]['condition'])
        return result

    def isSameCondition(self,state1,state2):
        for i in range(0,len(state1)):
            if state1[i]!=state2[i]:
                return False
        return True

    def subsumeClassifierToSet(self,offspring):
        sub_UUID=[]
        numSub=0
        for i in self.action_set:
            if (self.subsumes(i,offspring)):
                sub_UUID.append(i)
                numSub=numSub+1
                
        if numSub>0:
            numSub=random.randint(0,numSub-1)
            self.population[sub_UUID[numSub]]['numerosity']=self.population[sub_UUID[numSub]]['numerosity']+1
            #delete the offspring
            del self.population[offspring]
            return True
        return False

    #try to subsume the parents.
    def subsumeClassifier(self,offspring,parents):   
        for i in range(0,2):
            #print self.subsumes(parents[i],offspring)
            #if self.isSubsumer(parents[0]):
            #    print self.isSubsumer(parents[0])
            #    print self.isMoreGeneral(self.population[parents[0]]['condition'],self.population[offspring]['condition'])
            #    print self.population[parents[0]]['condition']
            #    print self.population[offspring]['condition']
            #    print self.subsumes(parents[i],offspring)
            #    print '=============================================================='
            if self.subsumes(parents[i],offspring):
                self.population[parents[i]]['numerosity']=self.population[parents[i]]['numerosity']+1 
                del self.population[offspring]           
                return
            result=self.subsumeClassifierToSet(offspring)
            # if any action set can subsume this offspring, then this offspring will be deleted
            if result:
                return
        self.addclassifierToSet(offspring)

    def addclassifierToSet(self,uuid):
        #check if the classifier exists already. If so, just increase the numerosity and free the space of the new classifier
        for i in self.population:
            if self.population[i]['action']==self.population[uuid]['action'] and self.isSameCondition(self.population[uuid]['condition'],self.population[i]['condition']):
                if i !=uuid:
                    #print "DO DO DO"
                    self.population[i]['numerosity']=self.population[i]['numerosity']+1
                    del self.population[uuid]
                    #print "DO DO DO~~~~~~~~"
                    #print self.population[i]['numerosity']
                    return


    ###################### offspring insertion #################################
    #Insert a discovered classifier into the population and respects the population size.
    def insertDiscoveredClassifier(self,offsprings, parents):
        
        if self.config.doGASubsumption:
            self.subsumeClassifier(offsprings[0],parents)
            self.subsumeClassifier(offsprings[1],parents)
        else:
            self.addclassifierToSet(offsprings[0])
            self.addclassifierToSet(offsprings[1])

        length=0
        for i in self.population:
            length=length+self.population[i]['numerosity']

        while length>self.config.maxPopSize:
            self.deleteStochClassifier_match_set()
            length=length-1
        #setsum=setsum+2
        #while setsum>self.config.maxPopSize:
        #    self.deleteStochClassifier_match_set()
        #    setsum=setsum-1
            

    def discoveryComponent(self,itTime,situation):
        fitsum=0.0
        setsum=0
        gaitsum=0

        # if the classifier set is empty, return (due to deletion)
        if self.action_set==None or len(self.action_set)==0:
            #print "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww"
            return

        #get all sums that are needed to do the discovery
        fitsum,setsum,gaitsum=self.getDiscoversSums()

        #do not do a GA is the average number of time-steps in the set since the last GA is less or equal than thetaGA
        if itTime-float(gaitsum)/float(setsum) <self.config.theta_GA:
            #print "111111111111111wwwwwwwwwwwwwwwwwwwww"
            return

        for i in self.action_set:
            self.population[i]['timeStamp']=itTime

        parents, offsprings=self.selectTwoClassifiers()

        #print len(parents)
        #print len(offsprings)

        self.crossover(offsprings)
        #print len(offsprings)

        for i in range(0,2):
            self.mutation(offsprings[i],situation)

        self.population[offsprings[0]]['prediction']=(self.population[offsprings[0]]['prediction']+self.population[offsprings[1]]['prediction'])/2.0
        self.population[offsprings[0]]['predictionError']=self.config.predictionErrorReduction*((self.population[offsprings[0]]['predictionError']+self.population[offsprings[1]]['predictionError'])/2.0)
        self.population[offsprings[0]]['fitness']=self.config.fitnessReduction*((self.population[offsprings[0]]['fitness']+self.population[offsprings[1]]['fitness'])/2.0)

        self.population[offsprings[1]]['prediction']=self.population[offsprings[0]]['prediction']
        self.population[offsprings[1]]['predictionError']=self.population[offsprings[0]]['predictionError']
        self.population[offsprings[1]]['fitness']=self.population[offsprings[0]]['fitness']

        #length=0
        #for i in range(0,len(self.classifier_population_set)):
        #    length=length+self.classifier_population_set[i].numerosity

        #print 'length',length
        self.insertDiscoveredClassifier(offsprings,parents)

    #print a single classifier to the string type
    def cover_classifier_to_string(self,uuid):
        result=''
        for i in range (0, len(self.population[uuid]['condition'])):
            result=result+str(self.population[uuid]['condition'][i])
        result=result+' : '
        result=result+str(self.population[uuid]['action'])
        result=result+' '
        result=result+'----> Numerosity: '+str(self.population[uuid]['numerosity'])+' '
        result=result+'Accuracy: '+str(round(self.population[uuid]['accuracy'],3))+' '
        result=result+'Fitness: '+str(round(self.population[uuid]['fitness'],3))+' '
        result=result+'Prediction Error: '+str(round(self.population[uuid]['predictionError'],3))+' '
        result=result+'Prediction: '+str(self.population[uuid]['prediction'])+' '
        result=result+'Experience: '+str(self.population[uuid]['experience'])+' '
        result=result+'ActionSetSize: '+str(round(self.population[uuid]['actionSetSize'],3))+'\n'
        return result

    def cover_classifier_to_string_2(self,input_dictionary):
        final_result=''
        result=''
        #print len(input_dictionary)
        for dic in input_dictionary:
            #print dic
            #print input_dictionary[dic]
            for i in range (0, len(input_dictionary[dic]['condition'])):
                result=result+str(input_dictionary[dic]['condition'][i])
            result=result+' : '
            result=result+str(input_dictionary[dic]['action'])
            result=result+' '
            result=result+'----> Numerosity: '+str(input_dictionary[dic]['numerosity'])+' '
            result=result+'Accuracy: '+str(round(input_dictionary[dic]['accuracy'],3))+' '
            result=result+'Fitness: '+str(round(input_dictionary[dic]['fitness'],3))+' '
            result=result+'Prediction Error: '+str(round(input_dictionary[dic]['predictionError'],3))+' '
            result=result+'Prediction: '+str(input_dictionary[dic]['prediction'])+' '
            result=result+'Experience: '+str(input_dictionary[dic]['experience'])+' '
            result=result+'ActionSetSize: '+str(round(input_dictionary[dic]['actionSetSize'],3))+'\n'
            final_result=final_result+ result
            result=''        
        return final_result

    def save_performance(self,name,txt):
        if name==None or name=='':
            f=open(self.savefolder,'wb')
        else:
            f=open(name,'wb')
        f.write(txt)
        f.close()

    def Header(self):
        format_time,Hour,Min,second=self.config.startTimer()
        print "Start Time:",format_time
        return Hour,Min,second
    
    def Exit(self,Hour,Min,second):
        format_time_1,Hour_1,Min_1,second_1=self.config.startTimer()
        print "shutting down"
        print "finish time: ",format_time_1
        use_time=self.config.elapsed(Hour_1,Hour,Min_1,Min,second_1,second)
        print use_time, "second"
        return use_time


    def doOneSingleStepProblemExplore(self,state, counter):
        #get the match set
        self.getMatchSet(state,counter)
        #calculate the prediction array
        predictionArray,sumClfrFitnessInPredictionArray= self.getPredictionArray()
        #Got the action winner based on randomly
        actionwinner=self.randomActionWinner(sumClfrFitnessInPredictionArray)
        #get the action set
        self.getActionSet(actionwinner)
        #calculate the reward
        reward=self.env.executeAction(actionwinner,self.config.execute_number,state)
        self.updateActionSet(0.0,reward)

        self.discoveryComponent(counter,state)
        self.match_set=[]
        self.action_set=[]

    #select the action in the prediction array with the best value
    def bestActionWinner(self,predictionArray):
        ret=0
        for i in range(1,self.config.numActions):
            if predictionArray[ret]<predictionArray[i]:
                ret=i
        return ret

    def doOneSingleStepProblemExploit(self,state,counter):
        self.getMatchSet(state,counter)
        #predictionArray,sumClfrFitnessInPredictionArray=self.getPredictionArray(mset)
        #actionWinner=self.bestActionWinner(predictionArray)
        #reward=self.env.executeAction(actionWinner,self.execute_number,state)
        self.match_set=[]
        self.action_set=[]

    def doOneSingleStepExperiment(self):
        explore=0
        for exploreProbC in range(0,self.config.maxproblemsize):
            explore=(explore+1)%2
            state=self.env.Create_Set_condition(self.config.condition_length)
            if explore==1:
                self.doOneSingleStepProblemExplore(state,exploreProbC)
            else:
                self.doOneSingleStepProblemExploit(state,exploreProbC)
        final_result=""
       
        #for r in self.population:
        #    final_result=final_result+self.cover_classifier_to_string(r)
        #self.save_performance('',final_result)
        sorted_result=self.sort_population()
        final_result=self.cover_classifier_to_string_2(sorted_result)
        #print final_result
        #print len(self.population)
        #print len(sorted_result)
        #final_result=self.cover_classifier_to_string_2(sorted_result)
        self.save_performance('',final_result)

    def startXCS(self):
        hour_1,min_1,second_1=self.Header()
        print "It is in progress! Please wait"
        self.doOneSingleStepExperiment()
        U_time=self.Exit(hour_1,min_1,second_1)
        self.save_time(str(U_time))

    def sort_population(self):
        sort_dict=copy.deepcopy(self.population)
        result={}       
        for i in range(0, len(sort_dict)):
            max=-100
            max_ID=None
            for  per in sort_dict: 
                if sort_dict[per]['numerosity']>max:
                    max=sort_dict[per]['numerosity']
                    max_ID=per
            if max_ID!=None:
                result.setdefault(i,sort_dict[max_ID])
                del sort_dict[max_ID]
            #print max
        return result

    def Read_Information(self,path):
        read_information=open(path,'r')
        information=[]
        for lines in read_information:
            if lines != '' and lines !='\n':
             information.append(lines)
        return information

    def Create_read_Classifier(self,numerosity,accuracy,fitness,predictionError,prediction,experience,setsize,condition,action):
        uuid_key=uuid.uuid1()
        classifier={'condition':condition,
                    'action':action,
                    'prediction':prediction,
                    'predictionError':predictionError,
                    'accuracy':accuracy,
                    'fitness':fitness,
                    'numerosity':numerosity,
                    'experience':experience,
                    'actionSetSize':setsize,
                    'timeStamp':0,                   
                    }
        self.population.setdefault(uuid_key,classifier)
        #return uuid_key

    def Get_basic_Details(self,informations):
        information=informations.split(' ')
        #print information
        
        results=[]
        
        for i in range(0,len(information)):
            if 'Numerosity:'in information[i]:
                results.append(int( information[i+1]))
            elif 'Accuracy:' in information[i]:
                results.append(float (information[i+1]))
            elif 'Fitness:' in information[i]:
                results.append(float(information[i+1]))
            elif 'Error:' in information[i]:
                results.append(float(information[i+1]))
            elif 'Prediction:' in information[i]:
                results.append(float(information[i+1]))
            elif 'Experience:' in information[i]:
                results.append(float(information[i+1]))
            elif 'ActionSetSize:' in information[i]:
                results.append(float(information[i+1]))
        
        state=[]
        for inf in information[0]:
            if inf=='0':
                state.append(0)
            elif inf=='1':
                state.append(1)
            elif inf=='#':
                state.append('#')
        results.append(state)
        results.append(int(information[2]))
        return results

    def get_Test_MatchSet(self,state):
        for i in self.population:
            if(self.isConditionMatched(self.population[i]['condition'],state)):
                #add matching classifier to the matchset
                self.match_set.append(i)


    def Test_exploit(self,Address):
        self.Read_xcs(Address)
        number_of_correct=0
        total_number=1000

        for i in range(0,total_number):
            state=self.env.Create_Set_condition(self.config.condition_length)
            self.get_Test_MatchSet(state)
            predictionArray,sumClfrFitnessInPredictionArray=self.getPredictionArray()
            actionWinner=self.bestActionWinner(predictionArray)

            reward=self.env.executeAction(actionWinner,self.config.execute_number,state)
            if reward>0:
                number_of_correct=number_of_correct+1
            self.match_set=[]

        print 100.0*number_of_correct/total_number ,'%'

    def Read_xcs(self,path):
        information =self.Read_Information(path)
        for inf in information:
            details=self.Get_basic_Details(inf)  
            self.Create_read_Classifier(details[0],details[1],details[2],details[3],details[4],details[5],details[6],details[7],details[8])


    def calculate_numerosity(self):
        number=0
        for i in self.population:
            number=number+self.population[i]['numerosity']
        print number

    def save_time(self,txt):
        f=open('result.txt','wb')
        f.write(txt)
        f.close()
class Test_xcs:
    def __init__(self):
        self.xcs=standard_XCS()
        self.env=environment()

    def print_population(self,population):
        for i in population:
            print 'uuid' ,i
            print 'action',self.xcs.population[i]['action']
            print 'condition',self.xcs.population[i]['condition']
            print 'prediction',self.xcs.population[i]['prediction']
            print 'predictionError',self.xcs.population[i]['predictionError']
            print 'accuracy',self.xcs.population[i]['accuracy']
            print 'fitness',self.xcs.population[i]['fitness']
            print 'numerosity',self.xcs.population[i]['numerosity']
            print 'experience',self.xcs.population[i]['experience']
            print 'actionSetSize',self.xcs.population[i]['actionSetSize']
            print 'timeStamp',self.xcs.population[i]['timeStamp']   

    def print_match_set(self):
        for i in range(0,len(self.xcs.match_set)):
            print self.xcs.match_set[i]
 
    def Test(self):
        #for i in range(0,10):
        #    state=[0,1,1,0,1,1]
        #    self.xcs.Create_Init_Classifier(state,1,1,1)

        #self.print_population()
        #self.print_population_action()
        for i in range(0,5000):
            #print i
            state=self.env.Create_Set_condition(6)
            #print state
            self.xcs.getMatchSet(state,i)
            p1,p2= self.xcs.getPredictionArray()
            actionwinner=self.xcs.randomActionWinner(p2)
            self.xcs.getActionSet(actionwinner)
            reward=self.env.executeAction(actionwinner,self.xcs.config.execute_number,state)
            self.xcs.updateActionSet(0.0,reward)
            #if i%500==0:
            #    self.print_population(parent)
            #    self.print_population(off)
            #    print "====================================================="
            #self.print_population(off)
            #self.xcs.twoPointCrossover(off)
            #self.xcs.mutation(off[0],state)
            #self.xcs.subsumes(parent[0],off[0])
            self.xcs.discoveryComponent(i,state)
            #print "####################################################"
            #self.print_population(off)
            self.xcs.match_set=[]
            self.xcs.action_set=[]
            #print "====================================================="
            #self.print_population(self.xcs.population)
            #print random.randint(0,2)
            #print self.xcs.randomActionWinner(p2)
        #print state
        #self.xcs.getMatchSet(state,3)
        #self.xcs.getActionSet(1)
        #self.xcs.updateActionSet(0.0,1000)
        print "====================================================="
        self.print_population(self.xcs.population)
        #self.print_match_set()
        #self.print_population(self.xcs.action_set)


    def Test_0(self):
        self.xcs.startXCS()

    def Test_1(self):
        Address='I:\\Standard_XCS\\Standard_XCS\\MUX_11_NEW.txt'
        Address_1='I:\\Standard_XCS\\Standard_XCS\\MUX_20.txt'
        self.xcs.Test_exploit(Address_1)
        self.xcs.calculate_numerosity()
        #self.xcs.config.finish()

Test=Test_xcs()
#Test.Test()
#print 0.1*pow(200/10,-5)
#print 2**1034
Test.Test_0()
#Test.Test_1()
#print uuid.uuid4()
