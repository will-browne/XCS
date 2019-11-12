import math
import types
class computer_operator:
    #number1
    def AND(self,input1,input2):
        return input1 and input2

    #number2
    def OR(self,input1,input2):
        return input1 or input2

    #number3
    def NOT(self,input):
        return int(not input)

    #number4
    def NOR(self,input1,input2):
        return int( not(input1 or input2))

    #number5
    def NAND(self,input1,input2):
        return int(not(input1 and input2))