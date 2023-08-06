from __future__ import annotations
from ast import comprehension
class rango:
    def __init__(self, strRange:str):
        try:
            self.lNumber = int(strRange[1:strRange.find(",")])
            self.lInclusive = True if strRange[0] == "[" else False
            self.rNumber = int(strRange[strRange.find(",")+1:-1])
            self.rInclusive= True if strRange[-1] == "]" else False

        except:
            raise Exception("Invalid String. May have invalid format, should be like this: [1,5)")
        assert self.lNumber <= self.rNumber, "right number should be greater than left"
    def contains(self, numbers: list):
        if (self.lInclusive and self.rInclusive == False): #si es inclusivo "["
            for num in numbers:
                if (self.lNumber<= num and self.rNumber > num):
                    return True
                else:
                    return False
                
        if (self.lInclusive and self.rInclusive == True): 
            for num in numbers:
                if (self.lNumber<= num and self.rNumber >= num):
                    return True
                else:
                    return False                    
        if (self.lInclusive == False and self.rInclusive == True): 
            for num in numbers:    
                if (self.lNumber< num and self.rNumber >= num):
                    return True    
                else:
                    return False                                    
        if (self.lInclusive == False and self.rInclusive == False): 
            for num in numbers: 
                if (self.lNumber< num and self.rNumber > num):
                    return True  
                else:
                    return False                              
        else:
            return False

    def getAllPoints(self):
        numbers = []
        if (self.lInclusive and self.rInclusive == False): 
            for i in range(self.lNumber,self.rNumber):
                numbers.append(i)
                
        if (self.lInclusive and self.rInclusive == True):
            for i in range(self.lNumber,self.rNumber+1):
                numbers.append(i)
                
        if (self.lInclusive == False and self.rInclusive == True):
            for i in range(self.lNumber+1,self.rNumber+1):
                numbers.append(i) 
                                   
        if (self.lInclusive == False and self.rInclusive == False): 
            for i in range(self.lNumber+1,self.rNumber):
                numbers.append(i)
                            
        return numbers

    def equals(self, compRange: rango):
        if(self.__dict__==compRange.__dict__):
            return True
        else:
            return False
        
    def endpoints(self): 
        endpoint = ()
        if (self.lInclusive and self.rInclusive == False): 
            endpoint = (self.lNumber, self.rNumber-1)
                
        if (self.lInclusive and self.rInclusive == True):
            endpoint = (self.lNumber, self.rNumber)
                
        if (self.lInclusive == False and self.rInclusive == True):
            endpoint = (self.lNumber+1, self.rNumber) 
                                   
        if (self.lInclusive == False and self.rInclusive == False): 
            endpoint = (self.lNumber+1, self.rNumber-1)
        return endpoint
    
    def containsRange(self, compRange:rango):
        

        if(not compRange.lInclusive):
            compRange.lNumber += 1
        if(not compRange.rInclusive):
            compRange.rNumber -= 1



        if (self.lInclusive and self.rInclusive == False): #[)
            if ((self.lNumber<= compRange.lNumber and self.rNumber > compRange.lNumber) and (self.lNumber<= compRange.rNumber and self.rNumber > compRange.rNumber)):
                return True
            else:
                return False
                
        if (self.lInclusive and self.rInclusive == True): #[]
            if ((self.lNumber<= compRange.lNumber and self.rNumber >= compRange.lNumber) and (self.lNumber<= compRange.rNumber and self.rNumber >= compRange.rNumber)):
                return True
            else:
                return False                    
        if (self.lInclusive == False and self.rInclusive == True):#(]
            if ((self.lNumber< compRange.lNumber and self.rNumber >= compRange.lNumber) and (self.lNumber< compRange.rNumber and self.rNumber >= compRange.rNumber)):
                return True    
            else:
                return False                                    
        if (self.lInclusive == False and self.rInclusive == False):#()
            if ((self.lNumber< compRange.lNumber and self.rNumber > compRange.lNumber) and (self.lNumber< compRange.rNumber and self.rNumber > compRange.rNumber)):
                return True  
            else:
                return False                              
        else:
            return False
    
    def overlapsRange(self, compRange: rango): 
        
        if(not compRange.lInclusive):
            compRange.lNumber += 1
        if(not compRange.rInclusive):
            compRange.rNumber -= 1
        
        if(not self.lInclusive):
            self.lNumber += 1
        if(not self.rInclusive):
            self.rNumber -= 1
            
        rOverlap = range(self.lNumber, self.rNumber+1)
        rComp =range(compRange.lNumber, compRange.rNumber+1)
        if (rOverlap.start <= rComp.stop and rComp.start <= rOverlap.stop):
            return True 
        else:
            return False



