class RangeClass:
    def __init__(self, range):
        self.range = range
    
    def split(self):
        firstInterval = self.range[0]
        firstNo = self.range[1:self.range.find(',')]
        secNo = self.range[self.range.find(',') + 1: -1]
        secInterval = self.range[-1]
        return [firstInterval, firstNo, secNo, secInterval]
    
    def range_validation(self):
        valid1 = (self.split()[0] == '(' or self.split()[0] == '[')
        valid2 = (self.split()[3] == ')' or self.split()[3] == ']')
        valid3 = (self.split()[1].isdigit() and self.split()[2].isdigit())
        valid4 = (int(self.split()[1]) <= int(self.split()[2]))
        if(valid1 == True and valid2 == True and valid3 == True and valid4 == True):
            return True
        else:
            return False
        
    def LenghtRange(self):
        L1 = int(self.split()[1])
        L2 = int(self.split()[2])
        if(self.split()[0] == '('):
            L1 += 1
        if(self.split()[3] == ']'):
            L2 += 1
        return range(L1, L2)
    
    def EndPoints(self):
        L1 = int(self.split()[1])
        L2 = int(self.split()[2])
        if(self.split()[0] == '('):
            L1 += 1
        if(self.split()[3] == ']'):
            L2 += 1
        return "{" + str(L1) + "," + str(L2 - 1) + "}"
    
    def allPoints(self):
        result = "{"
        var = self.LenghtRange()
        for i in var:
            if i < int(self.split()[2]) - 1 :
                result += str(i) + ","
            else:
                result += str(i)
        result += '}'
        return result
    
    def Equals(self, other: 'RangeClass'):
        var1 = self.LenghtRange()
        var2 = other.LenghtRange()
        if(var1 == var2):
            return True
        else:
            return False
    
    def overlapsRange(self, other: 'RangeClass'):
        choice = False
        var1 = self.LenghtRange()
        var2 = other.LenghtRange()
        for i in var1:
            for j in var2:
                if(i == j):
                    choice = True
        return choice
    
    



