from Config import standard_XCS_config
import random
import math
class environment:
    def __init__(self):
        self.config_set=standard_XCS_config()

    def Create_Set_condition(self,length):
        state=[0]*length
        for i in range(0, length):
            random_number=random.randint(0,1)
            if(random_number==0):
                state[i]=0
            else:
                state[i]=1
        return state

    # Multiplexer problem Notice use posBits in class environment_config_setting
    # Therefore, when the length of problem change, the value of posBits also need to be changed
    def execute_Multiplexer_Action(self,state):
        actual_Action=0
        place=self.config_set.posBits
        for i in range(0,self.config_set.posBits):
            if state[i]==1:
                place=place+int(math.pow(2.0,float(self.config_set.posBits-1-i)))
                #print place
        if state[place]==1:
            actual_Action=1
        return actual_Action
    
    
    #hidden even parity Notice use numRelevantBits and posRelevantBits in class environment_config_setting
    def execute_Hidden_Even_Parity_Action(self,state):
        actual_Action=0
        Numbers=0
        for i in range(0,self.config_set.numRelevantBits):
            if(state[self.config_set.posRelevantBits[i]]==1):
                Numbers=Numbers+1
        if Numbers%2==0:
            actual_Action=1
        return actual_Action
    
    #hidden odd parity attention lines similar to hidden even parity problem
    def execute_Hidden_Odd_Parity_Action(self,state):
        actual_Action=0
        Numbers=0
        for i in range(0,self.config_set.numRelevantBits):
            if(state[self.config_set.posRelevantBits[i]]==1):
                Numbers=Numbers+1
        if Numbers%2==1:
            actual_Action=1
        return actual_Action


    #count ones attention lines similar to hidden even parity problem
    def execute_Count_Ones_Action(self,state):
        actual_Action=0
        Numbers=0
        for i in range(0,self.config_set.numRelevantBits):
            if(state[self.config_set.posRelevantBits[i]]==1):
                Numbers=Numbers+1
        if Numbers>(self.config_set.numRelevantBits/2):
            actual_Action=1
        return actual_Action

    # carry problem
    def execute_Carry_Action(self,state):
        carry=0
        actual_Action=0
        half_condition=self.config_set.condition_length/2
        for i in range(0, half_condition):
            carry=(carry+int(state[half_condition-1-i])+int(state[half_condition-1-i+half_condition]))/2
        if carry==1:
            actual_Action=1
        return actual_Action


    # even_parity problem state is something like "10101", length depend on your setting
    def execute_Even_parity_Action(self,state):
        numbers=0
        actual_Action=0
        for i in range(0,len(state)):
            if state[i]==1:
                numbers=numbers+1
        if numbers%2==0:
            actual_Action=1
        return actual_Action


    # majority on problem
    def execute_Majority_On_Action(self,state):
        actual_Action=0
        Numbers=0
        for i in range(0,self.config_set.condition_length):
            if(state[i]==1):
                Numbers=Numbers+1
        if Numbers>(self.config_set.condition_length/2):
            actual_Action=1
        return actual_Action

    # DV1 problem
    def isDV1Term(self,n):
        for i in range(0,self.config_set.sizeDV1):
            if(n==self.config_set.DV1[i]):
                return True
        return False

    # DV1 problem
    def execute_DV1_Action(self,state):
        actualAction=0
        Number=0
        p=0
        for i in range(0,self.config_set.condition_length):
            Number=int(Number+int(state[self.config_set.condition_length-1-i])*math.pow(2,p))
            p=p+1
        #print Number
        if self.isDV1Term(Number):
            actualAction=1
        return actualAction

    # This function is for reinforcement learning     
    def executeAction(self, action, exenumber,state):

        #['multiplexer','hiddenEvenParity', 'hiddenOddParity', 'countOnes', 'carry', 'evenParity', 'majorityOn', 'dv1']
        if exenumber==0:
            result=self.execute_Multiplexer_Action(state)
        elif exenumber==1:
            result=self.execute_Hidden_Even_Parity_Action(state)
        elif exenumber==2: 
            result=self.execute_Hidden_Odd_Parity_Action(state)
        elif exenumber==3:
            result=self.execute_Count_Ones_Action(state)
        elif exenumber==4:
            result=self.execute_Carry_Action(state)
        elif exenumber==5:
            result=self.execute_Even_parity_Action(state)
        elif exenumber==6:
            result=self.execute_Majority_On_Action(state)
        elif exenumber==7:
            result=self.execute_DV1_Action(state)
        ret=0
        if result==action:
            ret=self.config_set.maxPayOff
        return ret

class Test_environment:
    def __init__(self):
        self.env=environment()
        self.config=standard_XCS_config()

    def Test_env(self):
        print "=============================================================="
        print " Create_Set_condition(self,length)"
        for i in range(0,10):
            state=self.env.Create_Set_condition(self.config.condition_length)
            #state=[1,0,1,0,1,1]
            print state
            action=self.env.execute_Multiplexer_Action(state)
            print action

            #action=self.env.execute_Hidden_Odd_Parity_Action(state)
            #print action
            #action=self.env.execute_Hidden_Odd_Parity_Action(state)
            #print action
            #action=self.env.execute_Count_Ones_Action(state)
            #print action
            #action=self.env.execute_Carry_Action(state)
            #print action
            #action=self.env.execute_Even_parity_Action(state)
            #print action
            #action=self.env.execute_Majority_On_Action(state)
            #print action
            #action=self.env.execute_DV1_Action(state)
            #print action
            result=self.env.executeAction(action,0,state)
            print result


#Test_env=Test_environment()
#Test_env.Test_env()
