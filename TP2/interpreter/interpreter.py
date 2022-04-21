from distutils.log import error
from lark.visitors import Interpreter
from lark import Tree,Token
import interpreter.utils as utils
import re

global identNumber

identNumber = 4

class MainInterpreter (Interpreter):

    def __init__(self):
        self.variables = dict() # var -> {state -> (declared, assigned, used), size -> int, datatype -> str, type -> str, keys -> list}
        self.warnings = []
        self.errors = []
        self.valueDataType = None
        self.valueSize = 0
        self.numDeclaredVars = {'atomic':0,'set':0,'list':0,'tuple':0,'dict':0}
        self.numInstructions = {'atribution':0,'read':0,'write':0,'condition':0,'cycle':0,'nestedControl':0}
        self.identLevel = 0
        self.controlDepth = 0
        self.maxcontrolDepth = 0
        self.ifData = None
        self.codeData = None
        

    def start(self,tree):
        # Visita todos os filhos em que cada um vão retornar o seu código
        res = self.visit_children(tree)

        self.analyzeVariablesDeclaredAndNotMentioned()

        self.errors = list(set(self.errors))
        self.warnings = list(set(self.warnings))
        statReport = utils.generateHTMLStatReport(self.numDeclaredVars,self.errors,self.warnings,self.numInstructions)

        utils.generateHTML(''.join(res[0]),statReport)

        output = dict()
        # Juntar o código dos vários blocos
        output["html"] = res[0]
        output["vars"] = self.variables

        return output

    def analyzeVariablesDeclaredAndNotMentioned(self):
        for (var,value) in self.variables.items():
            if value["state"][0] == True and value["state"][1] == False and value["state"][2] == False:
                self.warnings.append("Variável \"" + var + "\" declarada mas nunca mencionada")        
    
    def declaration(self,tree):
        r = self.visit(tree.children[0])
        return r

    def __generalDeclarationVisitor(self,tree,type):
        errors = []
        dataType = str(tree.children[0])
        varName = self.visit(tree.children[1])
        childNum = len(tree.children)

        # See if variable was mentioned in the code
        if varName not in self.variables:
            value = dict()
            value["state"] = [True,False,False]
            value["size"] = 0
            value["datatype"] = dataType
            self.variables[varName] = value

        else:

            value = self.variables[varName]

            # Case if variable declared
            if value["state"][0] == True:
                errors.append("Variável \"" + varName + "\" redeclarada")
            
            # Update variable status
            value["state"] = [True] + value['state'][1:]
                
        # if variable is assigned
        if childNum > 2:
            # Get value assigned to
            operand = self.visit(tree.children[2])

            if self.valueDataType != value['datatype']:
                errors.append("Tipo incorreto na atribuição da variável \"" + varName + "\"")

            else:
                value["size"] = self.valueSize
                value["state"][1] = True

            self.valueDataType = None # Useless but for bug-free programming
            self.valueSize = 0 # Useless but for bug-free programming

            if errors:
                self.errors.extend(errors)
                varName = utils.generateErrorTag(varName,";".join(errors))

            code = f"{dataType}{'' if type == 'atomic' else ' ' + type} {varName} = {operand};"

        else:

            if errors:
                self.errors.extend(errors)
                varName = utils.generateErrorTag(varName,";".join(errors))

            code = f"{dataType}{'' if type == 'atomic' else ' ' + type} {varName};"

        if not errors:
            self.numDeclaredVars[type] += 1

        return utils.generatePClassCodeTag(code)

    def grammar__declarations__atomic_declaration(self,tree):
        #print("atomic_decl_init")
        return self.__generalDeclarationVisitor(tree,"atomic")

    def grammar__declarations__set_declaration(self,tree):
        #print("set_declaration")
        return self.__generalDeclarationVisitor(tree,"set")

    def grammar__declarations__list_declaration(self,tree):
        #print("list_declaration")
        return self.__generalDeclarationVisitor(tree,"list")

    def grammar__declarations__tuple_declaration(self,tree):
        #print("tuple_declaration")
        return self.__generalDeclarationVisitor(tree,"tuple")

    def grammar__declarations__dict_declaration(self,tree):
        #print("dict_declaration")
        errors = []
        keyDataType = str(tree.children[0])
        valueDataType = str(tree.children[1])
        varName = self.visit(tree.children[2])
        childNum = len(tree.children)

        # See if variable was mentioned in the code
        if varName not in self.variables:
            value = dict()
            value["state"] = [True,False,False]
            value["size"] = 0
            value["datatype"] = (keyDataType,valueDataType)
            self.variables[varName] = value

        else:

            value = self.variables[varName]

            # Case if variable declared
            if value["state"][0] == True:
                errors.append("Variável \"" + varName + "\" redeclarada")
            
            # Update variable status
            value["state"] = [True] + value['state'][1:]
                
        # if variable is assigned
        if childNum > 3:
            # Get value assigned to
            operand = self.visit(tree.children[3])

            if self.valueDataType != value['datatype'] and self.valueSize != 0:
                errors.append("Tipo incorreto na atribuição da variável \"" + varName + "\"")

            else:
                value["size"] = self.valueSize
                value["state"][1] = True

            self.valueDataType = None # Useless but for bug-free programming
            self.valueSize = 0 # Useless but for bug-free programming

            if errors:
                self.errors.extend(errors)
                varName = utils.generateErrorTag(varName,";".join(errors))

            code = f"({keyDataType},{valueDataType}) dict {varName} = {operand};"

        else:

            if errors:
                self.errors.extend(errors)
                varName = utils.generateErrorTag(varName,";".join(errors))

            code = f"({keyDataType},{valueDataType}) dict {varName};"

        if not errors:
            self.numDeclaredVars['dict'] += 1

        return utils.generatePClassCodeTag(code)

    def grammar__declarations__var(self,tree):
        #print("var")
        return str(tree.children[0])

    def set(self,tree):
        #print("set")
        self.valueDataType = 'set'
        return f"{{{self.visit(tree.children[0])}}}"

    def list(self,tree):
        #print("list")
        self.valueDataType = 'list'
        return f"[{self.visit(tree.children[0])}]"

    def tuple(self,tree):
        #print("tuple")
        self.valueDataType = 'tuple'
        return f"({self.visit(tree.children[0])})"

    def dict(self,tree):
        #print("dict")
        self.valueDataType = 'dict'
        return f"{{{self.visit(tree.children[0])}}}"

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

    def grammar__declarations__dict_contents(self,tree):
        #print("dict_contents")
        keyDataType = set()
        valueDataType = set()
        repetitiveKeys = False
        valueKeys = []

        elemList = []
        for key,value in zip(tree.children[0::2], tree.children[1::2]):
            v_key = self.visit(key)
            keyDataType.add(self.valueDataType)
            v_value = self.visit(value)
            valueDataType.add(self.valueDataType)

            if v_key in valueKeys:
                repetitiveKeys = True
                break

            valueKeys.append(v_key)
            
            elemList.append(f"{v_key}:{v_value}")

        if repetitiveKeys:
            self.valueDataType = None
            return utils.generateErrorTag(",".join(elemList),"Dicionário tem chave repetida")

        self.valueSize = len(elemList)

        if len(valueDataType) > 1 or len(keyDataType) > 1:
            self.valueDataType = None
            return utils.generateErrorTag(",".join(elemList),"Tipos do dicionário não são uniformes")

        elif len(valueDataType) == 0 or len(keyDataType) == 0:
            self.valueDataType = None

        else:
            self.valueDataType = (keyDataType.pop(),valueDataType.pop())

        return ",".join(elemList)

    def grammar__declarations__dict_value(self,tree):
        #print("dict_value")
        return self.visit(tree.children[0])

    def grammar__declarations__operand_value(self,tree):
        #print("operand_value")
        return self.visit(tree.children[0])

    def grammar__declarations__operand_var(self,tree):
        #print("operand_var")
        varName = self.visit(tree.children[0])

        if varName not in self.variables:
            self.errors.append("Variável \"" + varName + "\" não declarada")
            varName = utils.generateErrorTag(varName,"Variável não declarada")

            self.valueDataType = ''
            self.valueSize = 0

            return varName

        value = self.variables[varName]

        if value["state"][1] == False:
            self.errors.append("Variável \"" + varName + "\" não atribuída")
            varName = utils.generateErrorTag(varName,"Variável não atribuída")

            self.valueDataType = ''
            self.valueSize = 0

            return varName

        value = self.variables[varName]
        value["state"][2] = True

        self.valueDataType = value["datatype"]
        self.valueSize = value["size"]

        return varName

    def grammar__declarations__value_string(self,tree):
        #print("value_string")
        self.valueDataType = "str"
        self.valueSize = 1
        return str(tree.children[0])

    def grammar__declarations__value_float(self,tree):
        #print("value_float")
        self.valueDataType = "float"
        self.valueSize = 1
        return str(tree.children[0])

    def grammar__declarations__value_int(self,tree):
        #print("value_int")
        self.valueDataType = "int"
        self.valueSize = 1
        return str(tree.children[0])

    def grammar__declarations__value_bool(self,tree):
        #print("value_bool")
        self.valueDataType = 'bool'
        self.valueSize = 1
        return str(tree.children[0])
    
    def code(self,tree):
        self.ifData = None
        r=list()
        for child in tree.children:
            r.append(self.visit(child))
        return r

    def instruction(self,tree):
        return self.visit(tree.children[0])

    def atribution(self,tree):

        ident = (self.identLevel * identNumber * " ")
               
        varName = self.visit(tree.children[0])

        exp = self.visit(tree.children[1])

        if varName not in self.variables:
            self.errors.append("Variável \"" + varName + "\" atribuida mas não declarada")
            varName = utils.generateErrorTag(varName,"Variável \"" + varName + "\" atribuída mas não declarada")
        
        elif not re.search(r'error',exp): 
            self.variables[varName]["state"][1] = True
            self.numInstructions['write'] += 1
            self.numInstructions['atribution'] += 1

        atrStr = f"{varName} = {exp};"

        self.codeData = atrStr
        
        return utils.generatePClassCodeTag(ident + atrStr)


    def condition(self,tree):
        identDepth = self.identLevel
        controlDepth = self.controlDepth
        self.controlDepth += 1
        if(controlDepth>0):
            self.numInstructions['nestedControl'] +=1

        self.identLevel += 1
        self.numInstructions['condition'] += 1

        # Cálculo da identação para pretty printing
        ident = (identDepth * identNumber * " ")

        cond = self.visit(tree.children[0])

        code = self.visit(tree.children[1])

        printCond = cond

        if self.ifData is not None and len(tree.children[1].children) == 1:
            cond = f'{cond} && {self.ifData[0]}'
            code = self.ifData[1]
            printCond = utils.generateSubTag(cond,"If conjugado")
            self.numInstructions['nestedControl'] -= 1
            self.numInstructions['condition'] -= 1
            

        self.ifData = (cond,code)

        taggedCode = utils.generatePClassCodeTag(ident + "if( "+printCond+") { // nivelDeControlo: "+str(controlDepth))
        taggedCode += ''.join(code)
        taggedCode +=utils.generatePClassCodeTag(ident + "}")

        self.identLevel = identDepth
        self.controlDepth = controlDepth

        return taggedCode

    def condition_else(self,tree):
        identDepth = self.identLevel
        controlDepth = self.controlDepth
        self.controlDepth += 1
        if(controlDepth>0):
            self.numInstructions['nestedControl'] +=1

        self.identLevel += 1
        self.numInstructions['condition'] += 1

        cond = self.visit(tree.children[0])
        code = self.visit(tree.children[1])
        elseCode = self.visit(tree.children[2])
        
        # Cálculo da identação para pretty #printing
        ident = (identDepth * identNumber * " ")


        taggedCode = utils.generatePClassCodeTag(ident + "if( "+cond+") { // nivelDeControlo: "+str(controlDepth))
        taggedCode += ''.join(code)
        taggedCode +=utils.generatePClassCodeTag(ident + "}")
        taggedCode +=utils.generatePClassCodeTag(ident + "else { // nivelDeControlo: " + str(controlDepth))
        taggedCode += ''.join(elseCode)
        taggedCode +=utils.generatePClassCodeTag(ident + "}")

        self.identLevel = identDepth
        self.controlDepth = controlDepth

        return taggedCode

    def cycle(self,tree):
        self.numInstructions['cycle'] += 1
        return self.visit(tree.children[0])

    def while_cycle(self,tree):
        identDepth = self.identLevel
        controlDepth = self.controlDepth
        self.controlDepth += 1
        if(controlDepth>0):
            self.numInstructions['nestedControl'] +=1
        self.maxcontrolDepth = self.maxcontrolDepth if self.maxcontrolDepth > controlDepth else controlDepth

        self.identLevel +=1
        
        # Cálculo da identação para pretty printing
        ident = (identDepth* identNumber * " ")

        bool=self.visit(tree.children[0])
        code=self.visit(tree.children[1])
        
        
        taggedCode = utils.generatePClassCodeTag(ident + "while(" + bool + ") { //nivelDeControlo: "+ str(controlDepth))
        taggedCode += ''.join(code)
        taggedCode += utils.generatePClassCodeTag(ident +"}")
        
        self.identLevel = identDepth
        self.controlDepth = controlDepth
        return taggedCode

    def do_while_cycle(self,tree):
        identDepth = self.identLevel
        controlDepth = self.controlDepth
        self.controlDepth += 1
        if(controlDepth>0):
            self.numInstructions['nestedControl'] +=1
        self.maxcontrolDepth = self.maxcontrolDepth if self.maxcontrolDepth > controlDepth else controlDepth

        self.identLevel +=1
        
        # Cálculo da identação para pretty printing
        ident = (identDepth* identNumber * " ")

        code=self.visit(tree.children[0])
        bool=self.visit(tree.children[1])

        taggedCode = utils.generatePClassCodeTag(ident + "do { //nivelDeControlo: "+str(controlDepth))
        taggedCode += ''.join(code)
        taggedCode += utils.generatePClassCodeTag(ident + "} while("+bool+")")
        
        self.identLevel = identDepth
        self.controlDepth = controlDepth

        return taggedCode

    def repeat_cycle(self,tree):
        identDepth = self.identLevel
        controlDepth = self.controlDepth
        self.controlDepth += 1
        if(controlDepth>0):
            self.numInstructions['nestedControl'] +=1
        self.maxcontrolDepth = self.maxcontrolDepth if self.maxcontrolDepth > controlDepth else controlDepth

        self.identLevel +=1
        
        # Cálculo da identação para pretty printing
        ident = (identDepth* identNumber * " ")

        mat=self.visit(tree.children[0])
        code=self.visit(tree.children[1])

        taggedCode = utils.generatePClassCodeTag(ident + "repeat(" + mat + ") { //nivelDeControlo: " + str(controlDepth))
        taggedCode += ''.join(code)
        taggedCode += utils.generatePClassCodeTag(ident + "}")
        
        self.identLevel = identDepth
        self.controlDepth = controlDepth


        return taggedCode
        
    def for_cycle(self,tree):

        identDepth = self.identLevel
        controlDepth = self.controlDepth
        self.controlDepth += 1
        if(controlDepth>0):
            self.numInstructions['nestedControl'] +=1
        self.maxcontrolDepth = self.maxcontrolDepth if self.maxcontrolDepth > controlDepth else controlDepth

        self.identLevel +=1
        
        # Cálculo da identação para pretty printing
        ident = (identDepth* identNumber * " ")

        childInfo = [None,None,None,None]

        for child in tree.children:
            if child.data == "atribution" and childInfo[0] is None:
                self.visit(child)
                childInfo[0] = self.codeData[:-1]
            elif child.data == "atribution" and childInfo[0] is not None:
                self.visit(child)
                childInfo[2] = self.codeData[:-1]
            elif child.data == 'boolexpr':
                self.visit(child)
                childInfo[1] = self.codeData[:-1]
            elif child.data == 'code':
                childInfo[3] = self.visit(child)

        insidePar = f'{"" if childInfo[0] is None else childInfo[0]};{"" if childInfo[1] is None else childInfo[1]};{"" if childInfo[2] is None else childInfo[2]}'

        taggedCode = utils.generatePClassCodeTag(ident + "for(" + insidePar + ") { //nivelDeControlo: " + str(controlDepth))
        taggedCode += ''.join(childInfo[3])
        taggedCode += utils.generatePClassCodeTag(ident + "}")
        
        self.identLevel = identDepth
        self.controlDepth = controlDepth


        return taggedCode


    def expression(self,tree):
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

        self.codeData = r
        
        return r

    def operand(self,tree):
        errors=[]
        value=self.visit(tree.children[0])
        
        if(tree.children[0].data=="var"):
            if value not in self.variables:
                errors.append("Variável \"" + value + "\" usada mas não declarada")

            elif self.variables[value]["state"][1] == False:
                errors.append("Variável \"" + value + "\" usada mas não inicializada")

            else:
                self.variables[value]["state"][2] = True
                self.numInstructions['read'] += 1
        
            
        if errors:
            self.errors.extend(errors)
            value = utils.generateErrorTag(value,";".join(errors))

        return value

    def value_string(self,tree):
        self.valueDataType = "str"
        return str(tree.children[0])

    def value_float(self,tree):
        self.valueDataType = "float"
        return str(tree.children[0])

    def value_int(self,tree):
        self.valueDataType = "int"
        return str(tree.children[0])

    def value_bool(self,tree):
        self.valueDataType = "bool"
        return str(tree.children[0])

    def var(self,tree):
        varName = str(tree.children[0])
        retStr = varName

        if(len(tree.children) > 1):
            operand = self.visit(tree.children[1])
            if self.valueDataType != "int":
                self.errors.append("Índice não é do tipo int")
                operand = utils.generateErrorTag(operand,"Índice não é do tipo int")
            retStr += '[' + operand + ']'

        if varName not in self.variables:
            self.valueDataType = None
        else:
            self.valueDataType = self.variables[varName]["datatype"]

        return retStr
    