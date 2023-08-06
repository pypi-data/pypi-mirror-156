# -*- coding: utf-8 -*-
"""
Created on Sat Jun 25 12:50:03 2022

@author: pannag
"""

import re

class RomanNumber:
    number=None
    
    def __init__(self):
        pass
    
    def convert(self,number):
        if type(number)==int:
            return self.__to_roman(number)
        elif type(number)==str:
            return self.__to_int(number)
        else:
            raise Exception("Error, cannot compute\n")
        
    def __ValidationOfRomanNumerals(self,number):
        try:
            return(bool(re.search(r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$",number)))
        except Exception:
            return False
     
    def __to_roman(self,number):
        if type(number)!=int:
            raise Exception(f"Expected Integer, got {type(number)}\n")
        string=""
        ro_values = {"I":1,"IV":4,"V":5,"IX":9,"X":10,"XL":40,"L":50,"CX":90,"C":100,"CD":400,"D":500,"CM":900,"M":1000}
        num = list(ro_values.values())
        roman = list(ro_values.keys())
        ro_string = []
        i=len(roman)-1
        while number:
            div = number // num[i]
            number %= num[i]
            while div:
                ro_string.append(roman[i])
                string+=roman[i]
                div -= 1
            i -= 1
        return string
    
    def __to_int(self,number):
        ro_values = {"I":1,"IV":4,"V":5,"IX":9,"X":10,"XL":40,"L":50,"CX":90,"C":100,"CD":400,"D":500,"CM":900,"M":1000}
        if not self.__ValidationOfRomanNumerals(number):
            raise Exception("Expected Roman string, Got an invalid input\n")
            return
        S = re.compile(r"(M{0,3})(CM|CD|D)?(C{0,3})(XC|XL|L)?(X{0,3})(IX|IV|V)?(I{0,3})")
        D = re.finditer(S,number)
        add=0
        value_holder=[]
        for i in D:
            for j in range(1,8):
                val = (i.group(j))
                if val!=None and val!='':
                    value_holder.append(val)
        if len(value_holder)>0:
            for i in value_holder:
                value = ro_values.get(i,None)
                if value:
                    add+=value
                else:
                    add+=ro_values.get(i[0],None)*i.count(i[0])
            return add
        return