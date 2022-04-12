from lark.visitors import Interpreter
from lark import Tree,Token
import re
import interpreter.utils as utils

global identLevel

identLevel = 4

class MainInterpreter (Interpreter):

    def __init__(self):
        self.nmrAtrib=0
        self.nmrRead=0
        self.nmrWrite=0
        self.nmrCond=0
        self.nmrCycle=0
        
        pass
    
    def start(self,tree):
        res=[]
        for child in tree.children:
            res+=self.visit(child)
        utils.generateHTML(''.join(res))
        #print(res)
        output = dict()
        # Juntar o código dos vários blocos
        output["html"] = ''.join(res)
        return output

    def code(self,tree):
        r=list()
        for child in tree.children:
            r.append(self.visit(child))

        return r

    def instruction_atribution(self,tree):
        r=""
        for child in tree.children:
            r+=self.visit(child)
        
        return r
    

    def instruction_condition(self,tree):
        self.nmrCond+=1
        self.nmrRead+=1
        
        return self.visit(tree.children[0])
    
    def instruction_cycle(self,tree):
        self.nmrCycle+=1
        return self.visit(tree.children[0])

    def atribution(self,tree):
        self.nmrWrite+=1
        self.nmrAtrib+=1
        var = self.visit(tree.children[0])
        exp = self.visit(tree.children[1])
        atrStr = f"{var} = {exp}"
        return utils.generatePClassCodeTag(atrStr)

    def condition(self,tree):
        cond = self.visit(tree.children[0])
        code = self.visit(tree.children[1])
        #print(code)
        taggedCode = utils.generatePClassCodeTag("if( "+cond+") {")
        taggedCode += ''.join(code)
        taggedCode +=utils.generatePClassCodeTag("}")
        
        return taggedCode

    def condition_else(self,tree):
        cond = self.visit(tree.children[0])
        code = self.visit(tree.children[1])
        elseCode = self.visit(tree.children[2])
        #print(code)
        taggedCode = utils.generatePClassCodeTag("if( "+cond+") {")
        taggedCode += ''.join(code)
        taggedCode +=utils.generatePClassCodeTag("}")
        taggedCode +=utils.generatePClassCodeTag("else{")
        taggedCode += ''.join(elseCode)
        taggedCode +=utils.generatePClassCodeTag("}")

        return taggedCode

    def cycle(self,tree):
        return self.visit(tree.children[0])

    def while_cycle(self,tree):
        
        bool=self.visit(tree.children[0])
        code=self.visit(tree.children[1])
        
        #if('instruction_condition' in tree.children[1]):
        #    print("instruction_condition")
        taggedCode = utils.generatePClassCodeTag("while(" + bool + ") {")
        taggedCode += ''.join(code)
        taggedCode += utils.generatePClassCodeTag("}")
        
        return taggedCode

    def do_while_cycle(self,tree):
        code=self.visit(tree.children[0])
        bool=self.visit(tree.children[1])

        taggedCode = utils.generatePClassCodeTag("do {")
        taggedCode += ''.join(code)
        taggedCode += utils.generatePClassCodeTag("} while("+bool+")")
        
        return taggedCode

    def repeat_cycle(self,tree):
        mat=self.visit(tree.children[0])
        code=self.visit(tree.children[1])

        taggedCode = utils.generatePClassCodeTag("repeat(" + mat + ") {")
        taggedCode += ''.join(code)
        taggedCode += utils.generatePClassCodeTag("}")
        
        return taggedCode
        
    def for_cycle(self,tree):
        #TODO
        bool=self.visit(tree.children[0])
        code=self.visit(tree.children[1])

        taggedCode = utils.generatePClassCodeTag("for(" + bool + " {")
        taggedCode += ''.join(code)
        taggedCode += utils.generatePClassCodeTag("}")
        
        return taggedCode
        

    def expression_var(self,tree):
        return self.visit(tree.children[0])


    def expression_boolexpr(self,tree):
        return self.visit(tree.children[0])

    def expression_matexpr(self,tree):
        return self.visit(tree.children[0])

    def matexpr(self,tree):
        r=""
        for child in tree.children:
            if(isinstance(child,Tree)):
                r+=self.visit(child)
            else:
                r+=child
        return r

    def simple_bool_expr(self,tree):
        left = self.visit(tree.children[0])
        center = tree.children[1]
        right = self.visit(tree.children[2])
        
        return f"{left} {center} {right}"


    def boolexpr(self,tree):
        r=""
        for child in tree.children:
            if(isinstance(child,Tree)):
                r+=self.visit(child)+" "
            else:
                r+=child+" "
        
        return r

    def operand(self,tree):
        value=self.visit(tree.children[0])
        return value

    def value_string(self,tree):
        return str(tree.children[0])

    def value_float(self,tree):
        return str(tree.children[0])

    def value_int(self,tree):
        return str(tree.children[0])

    def value_bool(self,tree):
        return str(tree.children[0])

    def var(self,tree):
        return str(tree.children[0])

    def var_struct(self,tree):
        word = tree.children[0]
        ind = tree.children[1]
        return f"{word}[{ind}]"
    
