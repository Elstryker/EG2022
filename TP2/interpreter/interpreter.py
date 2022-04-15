from lark.visitors import Interpreter
from lark import Tree,Token
import interpreter.utils as utils
import re

global identNumber

identNumber = 4

class MainInterpreter (Interpreter):

    def __init__(self):
        self.variables = dict() # var -> {state -> (declared, assigned, used), size -> int, datatype -> str, type -> str, keys -> list}
        self.canReplace = dict()
        self.warnings = []
        self.errors = []
        self.valueType = None
        self.valueDataType = None
        self.valueSize = 1
        self.nmrAtrib = 0
        self.nmrRead = 0
        self.nmrWrite = 0
        self.nmrCond = 0
        self.nmrCycle = 0
        self.identLevel = 0
        self.numberIfs = 0
        self.controlDepth = 0
        self.maxcontrolDepth = 0
        self.controlInside = 0

    def start(self,tree):
        # Visita todos os filhos em que cada um vão retornar o seu código
        res = self.visit_children(tree)
        utils.generateHTML(''.join(res[0]))

        output = dict()
        # Juntar o código dos vários blocos
        output["html"] = res[0]
        output["vars"] = self.variables
        output["warnings"] = self.warnings
        output["errors"] = self.errors
        output["controlInside"] = self.controlInside

        return output

    def declaration(self,tree):
        r = self.visit(tree.children[0])
        return r

    def grammar__declarations__atomic_declaration(self,tree):
        #print("atomic_decl_init")
        errors = []
        type = str(tree.children[0])
        varName = self.visit(tree.children[1])
        childNum = len(tree.children)

        # See if variable was mentioned in the code
        if varName not in self.variables:
            value = dict()
            value["state"] = [True,True,False] if childNum > 2 else [True,False,False]
            value["size"] = 1
            value["datatype"] = type
            value["type"] = "atomic"
            value["keys"] = []
            self.variables[varName] = value

        else:

            value = self.variables[varName]

            # Case if variable declared
            if value["state"][0] == True:
                errors.append("Variable \"" + varName + "\" redeclared")
            
            # Update variable status (depends if varibale is assigned)
            value["state"] = [True,True] + [value["state"][2]] if childNum > 2 else [True] + value['state'][1:]
                
        # if variable is assigned
        if childNum > 2:
            # Get value assigned to
            operand = self.visit(tree.children[2])

            if self.valueDataType != value['datatype']:
                errors.append("No correct typing in atribution of variable \"" + varName + "\"")

            self.valueDataType = None # Useless but for bug-free programming

            if errors:
                self.errors.extend(errors)
                varName = utils.generateErrorTag(varName,";".join(errors))

            code = f"{type} {varName} = {operand};"

        else:

            if errors:
                self.errors.extend(errors)
                varName = utils.generateErrorTag(varName,";".join(errors))

            code = f"{type} {varName};"

        return utils.generatePClassCodeTag(code)

    def grammar__declarations__set_declaration(self,tree):
        #print("set_declaration")
        errors = []
        type = str(tree.children[0])
        varName = self.visit(tree.children[1])
        childNum = len(tree.children)

        # See if variable was mentioned in the code
        if varName not in self.variables:
            value = dict()
            value["state"] = [True,True,False] if childNum > 2 else [True,False,False]
            value["size"] = 0
            value["datatype"] = type
            value["type"] = "set"
            value["keys"] = []
            self.variables[varName] = value

        else:

            value = self.variables[varName]

            # Case if variable declared
            if value["state"][0] == True:
                errors.append("Variable \"" + varName + "\" redeclared")
            
            # Update variable status (depends if varibale is assigned)
            value["state"] = [True,True] + [value["state"][2]] if childNum > 2 else [True] + value['state'][1:]
                
        # if variable is assigned
        if childNum > 2:
            # Get value assigned to
            operand = self.visit(tree.children[2])

            value["size"] = self.valueSize

            if self.valueDataType != value['datatype']:
                errors.append("No correct typing in atribution of variable \"" + varName + "\"")

            self.valueDataType = None # Useless but for bug-free programming
            self.valueSize = 1 # Useless but for bug-free programming

            if errors:
                self.errors.extend(errors)
                varName = utils.generateErrorTag(varName,";".join(errors))

            code = f"{type} set {varName} = {operand};"

        else:

            if errors:
                self.errors.extend(errors)
                varName = utils.generateErrorTag(varName,";".join(errors))

            code = f"{type} set {varName};"

        return utils.generatePClassCodeTag(code)

    def grammar__declarations__list_declaration(self,tree):
        #print("list_declaration")
        errors = []
        type = str(tree.children[0])
        varName = self.visit(tree.children[1])
        childNum = len(tree.children)

        # See if variable was mentioned in the code
        if varName not in self.variables:
            value = dict()
            value["state"] = [True,True,False] if childNum > 2 else [True,False,False]
            value["size"] = 0
            value["datatype"] = type
            value["type"] = "list"
            value["keys"] = []
            self.variables[varName] = value

        else:

            value = self.variables[varName]

            # Case if variable declared
            if value["state"][0] == True:
                errors.append("Variable \"" + varName + "\" redeclared")
            
            # Update variable status (depends if varibale is assigned)
            value["state"] = [True,True] + [value["state"][2]] if childNum > 2 else [True] + value['state'][1:]
                
        # if variable is assigned
        if childNum > 2:
            # Get value assigned to
            operand = self.visit(tree.children[2])

            value["size"] = self.valueSize

            if self.valueDataType != value['datatype']:
                errors.append("No correct typing in atribution of variable \"" + varName + "\"")

            self.valueDataType = None # Useless but for bug-free programming
            self.valueSize = 1 # Useless but for bug-free programming

            if errors:
                self.errors.extend(errors)
                varName = utils.generateErrorTag(varName,";".join(errors))

            code = f"{type} list {varName} = {operand};"

        else:

            if errors:
                self.errors.extend(errors)
                varName = utils.generateErrorTag(varName,";".join(errors))

            code = f"{type} list {varName};"

        return utils.generatePClassCodeTag(code)

    def grammar__declarations__tuple_declaration(self,tree):
        #print("tuple_declaration")
        errors = []
        type = str(tree.children[0])
        varName = self.visit(tree.children[1])
        childNum = len(tree.children)

        # See if variable was mentioned in the code
        if varName not in self.variables:
            value = dict()
            value["state"] = [True,True,False] if childNum > 2 else [True,False,False]
            value["size"] = 0
            value["datatype"] = type
            value["type"] = "tuple"
            value["keys"] = []
            self.variables[varName] = value

        else:

            value = self.variables[varName]

            # Case if variable declared
            if value["state"][0] == True:
                errors.append("Variable \"" + varName + "\" redeclared")
            
            # Update variable status (depends if varibale is assigned)
            value["state"] = [True,True] + [value["state"][2]] if childNum > 2 else [True] + value['state'][1:]
                
        # if variable is assigned
        if childNum > 2:
            # Get value assigned to
            operand = self.visit(tree.children[2])

            value["size"] = self.valueSize

            if self.valueDataType != value['datatype']:
                errors.append("No correct typing in atribution of variable \"" + varName + "\"")

            self.valueDataType = None # Useless but for bug-free programming
            self.valueSize = 1 # Useless but for bug-free programming

            if errors:
                self.errors.extend(errors)
                varName = utils.generateErrorTag(varName,";".join(errors))

            code = f"{type} tuple {varName} = {operand};"

        else:

            if errors:
                self.errors.extend(errors)
                varName = utils.generateErrorTag(varName,";".join(errors))

            code = f"{type} tuple {varName};"

        return utils.generatePClassCodeTag(code)

    def grammar__declarations__dict_declaration(self,tree): #TODO
        #print("dict_declaration")
        return self.visit_children(tree)

    def grammar__declarations__var(self,tree):
        #print("var")
        return str(tree.children[0])

    def grammar__declarations__set(self,tree):
        #print("set")
        return self.visit(tree.children[0])

    def grammar__declarations__list(self,tree):
        #print("list")
        return self.visit(tree.children[0])

    def grammar__declarations__tuple(self,tree):
        #print("tuple")
        return self.visit(tree.children[0])

    def grammar__declarations__dict(self,tree):
        #print("dict")
        return self.visit(tree.children[0])

    def grammar__declarations__list_contents(self,tree):
        #print("list_contents")
        return self.visit(tree.children[0])

    def grammar__declarations__int_contents(self,tree):
        #print("int_contents")
        self.valueDataType = 'int'
        self.valueSize = len(tree.children)
        elemList = []
        for child in tree.children:
            elemList.append(str(child))
        return ",".join(elemList)

    def grammar__declarations__float_contents(self,tree):
        #print("float_contents")
        self.valueDataType = 'float'
        self.valueSize = len(tree.children)
        elemList = []
        for child in tree.children:
            elemList.append(str(child))
        return ",".join(elemList)

    def grammar__declarations__string_contents(self,tree):
        #print("string_contents")
        self.valueDataType = 'str'
        self.valueSize = len(tree.children)
        elemList = []
        for child in tree.children:
            elemList.append(str(child))
        return ",".join(elemList)

    def grammar__declarations__bool_contents(self,tree):
        #print("bool_contents")
        self.valueDataType = 'bool'
        self.valueSize = len(tree.children)
        elemList = []
        for child in tree.children:
            elemList.append(str(child))
        return ",".join(elemList)

    def grammar__declarations__dict_contents(self,tree): #TODO
        #print("dict_contents")
        return self.visit_children(tree)

    def grammar__declarations__operand_value(self,tree):
        #print("operand_value")
        return self.visit(tree.children[0])

    def grammar__declarations__operand_var(self,tree): #TODO
        #print("operand_var")
        return self.visit_children(tree)

    def grammar__declarations__value_string(self,tree):
        #print("value_string")
        self.valueType = "atomic"
        self.valueDataType = "str"
        return str(tree.children[0])

    def grammar__declarations__value_float(self,tree):
        #print("value_float")
        self.valueType = "atomic"
        self.valueDataType = "float"
        return str(tree.children[0])

    def grammar__declarations__value_int(self,tree):
        #print("value_int")
        self.valueType = "atomic"
        self.valueDataType = "int"
        return str(tree.children[0])

    def grammar__declarations__value_bool(self,tree):
        #print("value_bool")
        self.valueType = "atomic"
        self.valueDataType = 'bool'
        return str(tree.children[0])
    
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
        self.nmrWrite += 1
        self.nmrAtrib+=1
        errors = []
        ident = (self.identLevel * identNumber * " ")

        #if tree.children[0].data =="var":
        varName = self.visit(tree.children[0])
        #else:
            #varName = self.visit(tree.children[0])
            #varName = tree.children[0].children[0]
            #index = tree.children[0].children[1]
            
       
        exp = self.visit(tree.children[1])

        if varName in self.variables:
            self.variables[varName]["state"][2] = True
            
        else:
            value = dict()
            value["state"] = [False,False,True]
            value["size"]=0
            value["datatype"]= None
            value["type"] = None
            value["keys"] = []
            self.variables[varName] = value
            
        
        value =self.variables[varName]
        if value["state"][0]==False and value["state"][2]==True:
            errors.append("Variable \"" + varName +"\" used but not initialized")
            
        if errors:
            self.errors.extend(errors)
            varName = utils.generateErrorTag(varName,";".join(errors))
         
        atrStr = f"{varName} = {exp};"

        return utils.generatePClassCodeTag(ident + atrStr)

    def condition(self,tree):
        identDepth = self.identLevel
        controlDepth = self.controlDepth
        self.controlDepth += 1
        if(controlDepth>1):
            self.controlInside +=1
        self.maxcontrolDepth = self.maxcontrolDepth if self.maxcontrolDepth > controlDepth else controlDepth

        self.identLevel += 1
        self.numberIfs += 1

        # Cálculo da identação para pretty #printing
        ident = (identDepth * identNumber * " ")

        cond = self.visit(tree.children[0])
        code = self.visit(tree.children[1])
        catchBool = re.search(r'\<p class=\"code\">\n\s*(if\(\s*(.*)\)\s*{\s*\/\/controlLevel\: \d+)\n<\/p>\n',code[0])
        if catchBool and catchBool.group(2) in self.canReplace:
            cond += " && " + catchBool.group(2)
            code[0]= code[0].replace(catchBool.group(0),"")
            code[0] = re.sub(r"\<p class=\"code\"\>\n\s*}\n\<\/p\>\n","",code[0])
            wasChanged = re.search(r'\n(.*)\$IF conjugado</span></div>',code[0])
            if(wasChanged):
                code[0] = re.sub(r'\n(.*)\$IF conjugado</span></div>',"\n"+utils.generateSubTag(catchBool.group(2))+"<div class",code[0])
            else:
                code[0] = re.sub(r'\n\s*<div class',"\n"+utils.generateSubTag(catchBool.group(2))+"<div class",code[0])
        

        self.canReplace[cond] = code

        taggedCode = utils.generatePClassCodeTag(ident + "if( "+cond+") { //controlLevel: "+str(controlDepth))
        taggedCode += ''.join(code)
        taggedCode +=utils.generatePClassCodeTag(ident + "}")

        self.identLevel = identDepth
        self.controlDepth = controlDepth
        
        return taggedCode

    def condition_else(self,tree):

        identDepth = self.identLevel
        controlDepth = self.controlDepth
        self.controlDepth += 1
        if(controlDepth>1):
            self.controlInside +=1
        self.maxcontrolDepth = self.maxcontrolDepth if self.maxcontrolDepth > controlDepth else controlDepth

        self.identLevel += 1
        self.numberIfs += 1

        cond = self.visit(tree.children[0])
        code = self.visit(tree.children[1])
        elseCode = self.visit(tree.children[2])
        
        # Cálculo da identação para pretty #printing
        ident = (identDepth * identNumber * " ")


        taggedCode = utils.generatePClassCodeTag(ident + "if( "+cond+") { // controlLevel: "+str(controlDepth))
        taggedCode += ''.join(code)
        taggedCode +=utils.generatePClassCodeTag(ident + "}")
        taggedCode +=utils.generatePClassCodeTag(ident + "else { // controlLevel: " + str(controlDepth))
        taggedCode += ''.join(elseCode)
        taggedCode +=utils.generatePClassCodeTag(ident + "}")

        self.identLevel = identDepth
        self.controlDepth = controlDepth

        return taggedCode

    def cycle(self,tree):
        return self.visit(tree.children[0])

    def while_cycle(self,tree):
        identDepth = self.identLevel
        controlDepth = self.controlDepth
        self.controlDepth += 1
        if(controlDepth>1):
            self.controlInside +=1
        self.maxcontrolDepth = self.maxcontrolDepth if self.maxcontrolDepth > controlDepth else controlDepth

        self.identLevel +=1
        
        # Cálculo da identação para pretty printing
        ident = (identDepth* identNumber * " ")

        bool=self.visit(tree.children[0])
        code=self.visit(tree.children[1])
        
        
        taggedCode = utils.generatePClassCodeTag(ident + "while(" + bool + ") { //controlLevel: "+ str(controlDepth))
        taggedCode += ''.join(code)
        taggedCode += utils.generatePClassCodeTag(ident +"}")
        
        self.identLevel = identDepth
        self.controlDepth = controlDepth
        return taggedCode

    def do_while_cycle(self,tree):
        identDepth = self.identLevel
        controlDepth = self.controlDepth
        self.controlDepth += 1
        if(controlDepth>1):
            self.controlInside +=1
        self.maxcontrolDepth = self.maxcontrolDepth if self.maxcontrolDepth > controlDepth else controlDepth

        self.identLevel +=1
        
        # Cálculo da identação para pretty printing
        ident = (identDepth* identNumber * " ")
        identCode = ((identDepth+1)* identNumber * " ")

        code=self.visit(tree.children[0])
        bool=self.visit(tree.children[1])

        taggedCode = utils.generatePClassCodeTag(ident + "do { //controlLevel: "+str(controlDepth))
        taggedCode += ''.join(identCode + code)
        taggedCode += utils.generatePClassCodeTag(ident + "} while("+bool+")")
        
        self.identLevel = identDepth
        self.controlDepth = controlDepth

        return taggedCode

    def repeat_cycle(self,tree):
        identDepth = self.identLevel
        controlDepth = self.controlDepth
        self.controlDepth += 1
        if(controlDepth>1):
            self.controlInside +=1
        self.maxcontrolDepth = self.maxcontrolDepth if self.maxcontrolDepth > controlDepth else controlDepth

        self.identLevel +=1
        
        # Cálculo da identação para pretty printing
        ident = (identDepth* identNumber * " ")
        identCode = ((identDepth+1)* identNumber * " ")
        mat=self.visit(tree.children[0])
        code=self.visit(tree.children[1])

        taggedCode = utils.generatePClassCodeTag(ident + "repeat(" + mat + ") { //controlLevel: " + str(controlDepth))
        taggedCode += ''.join(identCode + code)
        taggedCode += utils.generatePClassCodeTag(ident + "}")
        
        self.identLevel = identDepth
        self.controlDepth = controlDepth


        return taggedCode
        
    def for_cycle(self,tree):

        identDepth = self.identLevel
        controlDepth = self.controlDepth
        self.controlDepth += 1
        if(controlDepth>1):
            self.controlInside +=1
        self.maxcontrolDepth = self.maxcontrolDepth if self.maxcontrolDepth > controlDepth else controlDepth

        self.identLevel +=1
        
        # Cálculo da identação para pretty printing
        ident = (identDepth* identNumber * " ")
        identCode = ((identDepth+1)* identNumber * " ")
        
        size = len(tree.children)
        insidePar = "<p class=\"code\">\n"
        for i in range(size-1):
            getCode = self.visit(tree.children[i])
            findCode = re.search(r"\<p class=\"code\"\>\n\s*((.*))\n\<\/p\>",getCode)
            if findCode:
                if i == size-2:
                    sub=findCode.group(1).replace(";","")
                    insidePar += sub
                else:
                    insidePar += findCode.group(1)
                    
            else:
                if(not i==size-2):
                    insidePar += getCode
                    insidePar +=";"
       
        insidePar = insidePar.replace(";;",";")

        code=self.visit(tree.children[1])

        taggedCode = utils.generatePClassCodeTag(ident + "for(" + insidePar + ") { // controlLevel: " + str(controlDepth))
        taggedCode += utils.generatePClassCodeTag(identCode + code)
        taggedCode += utils.generatePClassCodeTag(ident + "}")
        
        self.identLevel = identDepth
        self.controlDepth = controlDepth


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
        errors=[]
        value=self.visit(tree.children[0])
        
        if(tree.children[0].data=="var"):
            if value not in self.variables or self.variables[value]["state"][0]==False:
                errors.append("Variable \"" + value + "\" used but not initialized")
            
        if errors:
            self.errors.extend(errors)
            value = utils.generateErrorTag(value,";".join(errors))

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
    