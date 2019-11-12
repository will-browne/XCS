import random
import uuid
import time
import copy
from Config import XCSCFC_config
from Environment import environment
from computer_operator import computer_operator

class codeFragment:
    def __init__(self,Address):
        self.config=XCSCFC_config()
        self.split_arrow='  --------->'
        self.date_str='D'
        self.CF_str='CF_'
        self.hardcode_function=computer_operator()
        self.startingPreviousCFID=0
        self.numPreviousCFs=0
        self.Previous_CFs={}
        self.initializeCFPopulation(Address)

    def initializeCFPopulation(self,Address):
        if self.config.currentProblemLevel>1:
            self.getPreviousCFpopulation(Address,self.Previous_CFs)

    def Initial_CodeFragment(self,Input_dictionary,key,codeFragment):
        CF={'codeFragment': codeFragment,'dontcare':False}
        Input_dictionary.setdefault(key,CF)

    def createNewCF(self,key,dictionary):
        CF=[]
        for i in range(0,self.config.cfMaxLength):
            CF.append(self.config.OPNOP)
        self.Initial_CodeFragment(dictionary,key,CF)

    def Read_Information(self,path):
        read_information=open(path,'r')
        information=[]
        for lines in read_information:
            if lines != '' and lines !='\n':
             information.append(lines)
        return information

    def getPreviousCFpopulation(self,Address,Dictionary):
        Information=self.Read_Information(Address)
        #maximum number of stored CFs
        self.numPreviousCFs=  int(Information[0].split('\n')[0])
        #print numPreviousCFs
        #starting ID number of previous CFs
        self.startingPreviousCFID=int(Information[1].split('\n')[0])
        #print startingPreviousCFID
        #ID number for storing
        ID=self.config.condLength
        for i in range(2,len(Information)):
            PCF= Information[i].split(self.split_arrow)[0].split(' ')
            CF=[]
            for inf in PCF:
                CF.append(self.getOpType(inf))
            if not self.isExists(CF,Dictionary):
                self.Initial_CodeFragment(Dictionary,ID,CF)
                ID=ID+1
        self.numPreviousCFs=ID


    def isExists(self,CF,CF_population):
        for i in CF_population:
            if CF_population[i]['codeFragment']==CF:
                return True
        return False
    
    def getOpType(self,inf):
        if inf==self.config.OPNOP_str:
            return self.config.OPNOP
        if inf==self.config.OPAND_str:
            return self.config.OPAND
        if inf==self.config.OPOR_str:
            return self.config.OPOR
        if inf==self.config.OPNAND_str:
            return self.config.OPNAND
        if inf==self.config.OPNOR_str:
            return self.config.OPNOR
        if inf==self.config.OPNOT_str:
            return self.config.OPNOT
        if self.date_str in inf:
            result= int( inf.split(self.date_str)[-1])
            return result
        if self.CF_str in inf:
            result= int( inf.split(self.CF_str)[-1])+(self.config.condLength-self.startingPreviousCFID)
            return result

    def isDontcareCF(self,dictionary,id):
         if dictionary[id]['dontcare']==True:
             return True
         return False

    def numberOfNonDontcares(self,dictionary):
         number=0
         for i in dictionary:
             if dictionary[i]['dontcare']==False:
                 number=number+1
         return number

    def getNumberOfArguments(self,code):
        if code==self.config.OPAND:
            return 2
        elif code==self.config.OPOR:
            return 2
        elif code==self.config.OPNAND:
            return 2
        elif code==self.config.OPNOR:
            return 2
        elif code==self.config.OPNOT:
            return 1
        else:
            return 0

    def DepthMax(self,starpoint,CF):
        if starpoint<0:
            return 0
        if self.getNumberOfArguments(CF[starpoint])==0:
            return 0
        if self.getNumberOfArguments(CF[starpoint])==1:
            leftDepth=self.DepthMax(starpoint-1,CF)
            rightDepth=0
        if self.getNumberOfArguments(CF[starpoint])==2:
            leftDepth=self.DepthMax(starpoint-1,CF)
            distance=2+self.getNumberOfArguments(CF[starpoint-1])
            rightDepth=self.DepthMax(starpoint-distance,CF)
        if leftDepth>rightDepth:
            return leftDepth+1
        if leftDepth<=rightDepth:
            return rightDepth+1

    def validateDepth(self,CF):
        startpoint=len(CF)-2
        depth=self.DepthMax(startpoint,CF)
        if depth<=self.config.cfMaxDepth:
            return True
        else:
            return False

    def isPreviousLevelsCode(self,code):
        if self.config.currentProblemLevel>1:
            if code>=self.config.condLength and code<self.numPreviousCFs:
                return True
            else:
                return False
        return False

    def evaluateCF(self,startpoint,CF,state):
        if startpoint<0:
            print "CF error"
        if CF[startpoint]==self.config.OPNOP:
            startpoint=startpoint-1
            result=self.evaluateCF(startpoint,CF,state)
            return result
        elif CF[startpoint]>=0 and CF[startpoint]<self.config.condLength:
            return state[CF[startpoint]]

        elif self.isPreviousLevelsCode(CF[startpoint]):
            new_cf=self.Previous_CFs[CF[startpoint]]['codeFragment']
            new_startpoint=len(new_cf)-1
            result=self.evaluateCF(new_startpoint,new_cf,state)
            return result

        elif CF[startpoint]==self.config.OPNOT:
            lEFT=self.evaluateCF(startpoint-1,CF,state)
            return self.hardcode_function.NOT(lEFT)

        elif CF[startpoint]==self.config.OPAND:
            LEFT= self.evaluateCF(startpoint-1,CF,state)
            distance=2+self.getNumberOfArguments(CF[startpoint-1])
            RIGHT=self.evaluateCF(startpoint-distance,CF,state)
            return self.hardcode_function.AND(LEFT,RIGHT)

        elif CF[startpoint]==self.config.OPOR:
            LEFT= self.evaluateCF(startpoint-1,CF,state)
            distance=2+self.getNumberOfArguments(CF[startpoint-1])
            RIGHT=self.evaluateCF(startpoint-distance,CF,state)
            return self.hardcode_function.OR(LEFT,RIGHT)

        elif CF[startpoint]==self.config.OPNOR:
            LEFT= self.evaluateCF(startpoint-1,CF,state)
            distance=2+self.getNumberOfArguments(CF[startpoint-1])
            RIGHT=self.evaluateCF(startpoint-distance,CF,state)
            return self.hardcode_function.NOR(LEFT,RIGHT)

        elif CF[startpoint]==self.config.OPNAND:
            LEFT= self.evaluateCF(startpoint-1,CF,state)
            distance=2+self.getNumberOfArguments(CF[startpoint-1])
            RIGHT=self.evaluateCF(startpoint-distance,CF,state)
            return self.hardcode_function.NAND(LEFT,RIGHT)
        else:
            print "CF system error"

    def validLeaf(self,code):
        if code>=0 and code<self.config.condLength:
            return code
        if self.isPreviousLevelsCode(code):
            return code
        return -1

    def leafname(self,code):
        if code>=0 and code<self.config.condLength:
            return self.date_str+str(code)
        elif self.isPreviousLevelsCode(code):
            return self.CF_str+str(code)
        else:
            return 'invalid leaf name'
            print 'invalid leaf name'

    def opchar(self,code):
        if self.validLeaf(code)>=0:
            return self.leafname(code)
        elif code==self.config.OPAND:
            return self.config.OPAND_str
        elif code==self.config.OPOR:
            return self.config.OPOR_str
        elif code==self.config.OPNAND:
            return self.config.OPNAND_str
        elif code==self.config.OPNOR:
            return self.config.OPNOR_str
        elif code==self.config.OPNOT:
            return self.config.OPNOT_str
        elif code==self.config.OPNOP:
            return self.config.OPNOP_str
        else:
            return 'invalid leaf system error'

    def turn_to_char(self,CF):
        result=[]
        for i in range(0,len(CF)):
            result.append(self.opchar(CF[i]))
        return result

class Test:
    def __init__(self):
        
        self.CFs={}
        self.Address='I:\\Summer 2015\\xcsCFCavg\\0\\11MUXCFs.txt'
        self.XCSCFC=codeFragment(self.Address)

    def Print_CF(self,Dict):
        for i in Dict:
            print 'Key: ',i, 'CF:', Dict[i]['codeFragment']

    def CF_Test(self):
        #for i in range(0,10):
        #    self.XCSCFC.createNewCF(i,self.CFs)
        #print self.CFs
        #result= self.XCSCFC.Read_Information(self.Address)
        #print result[0]
        #print result[1]
        #self.XCSCFC.getPreviousCFpopulation(self.Address,self.CFs)
        print self.XCSCFC.numPreviousCFs
        self.Print_CF(self.XCSCFC.Previous_CFs)
        #print self.XCSCFC.numberOfNonDontcares(self.CFs)
        for i in self.XCSCFC.Previous_CFs:
            state_1=[0,0,0,0,0,0,0,0,0,0,0]
            T_CF=self.XCSCFC.Previous_CFs[i]['codeFragment']
            startpoint=len(T_CF)-1
            print 'Key: ',i
            print 'CF :', self.XCSCFC.turn_to_char(T_CF)
            print 'resu;t :  ',self.XCSCFC.evaluateCF(startpoint,T_CF,state_1)
            print 'depth :',self.XCSCFC.DepthMax(startpoint-1,T_CF)
        
        #startpoint=len(CF)-2
        print T_CF
        #print startpoint
        #r=self.XCSCFC.DepthMax(startpoint,CF)
        #print self.XCSCFC.validateDepth(CF)
T=Test()
T.CF_Test()
#print random.randint(0,10000)