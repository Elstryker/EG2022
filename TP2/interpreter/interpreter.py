from lark.visitors import Interpreter
from lark import Tree,Token
import re
import interpreter.utils as utils

global identLevel

identLevel = 4

class MainInterpreter (Interpreter):

    def __init__(self):
        self.variables = dict() # var -> {state -> (declared, assigned, used), size -> int, datatype -> str, type -> str, keys -> list}
        self.warnings = []
        self.errors = []
        self.valueDataType = None
        self.valueSize = 0
        self.valueKeys = []
        self.numDeclaredVars = dict()
        self.numDeclaredVars['atomic'] = 0
        self.numDeclaredVars['set'] = 0
        self.numDeclaredVars['list'] = 0
        self.numDeclaredVars['tuple'] = 0
        self.numDeclaredVars['dict'] = 0
        self.nmrAtrib=0
        self.nmrRead=0
        self.nmrWrite=0
        self.nmrCond=0
        self.nmrCycle=0

    def start(self,tree):
        # Visita todos os filhos em que cada um vão retornar o seu código
        res = self.visit_children(tree)

        utils.generateHTML(''.join(res[0]))

        output = dict()
        # Juntar o código dos vários blocos
        output["html"] = ''.join(res[0])
        output["vars"] = self.variables
        output["warnings"] = self.warnings
        output["errors"] = self.errors
        output["numDeclaredVars"] = self.numDeclaredVars

        return output

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
            value["type"] = type
            value["keys"] = []
            self.variables[varName] = value

        else:

            value = self.variables[varName]

            # Case if variable declared
            if value["state"][0] == True:
                errors.append("Variable \"" + varName + "\" redeclared")
            
            # Update variable status
            value["state"] = [True] + value['state'][1:]
                
        # if variable is assigned
        if childNum > 2:
            # Get value assigned to
            operand = self.visit(tree.children[2])

            if self.valueDataType != value['datatype']:
                errors.append("No correct typing in atribution of variable \"" + varName + "\"")

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
            value["type"] = 'dict'
            value["keys"] = []
            self.variables[varName] = value

        else:

            value = self.variables[varName]

            # Case if variable declared
            if value["state"][0] == True:
                errors.append("Variable \"" + varName + "\" redeclared")
            
            # Update variable status
            value["state"] = [True] + value['state'][1:]
                
        # if variable is assigned
        if childNum > 3:
            # Get value assigned to
            operand = self.visit(tree.children[3])

            if self.valueDataType != value['datatype'] and self.valueSize != 0:
                errors.append("No correct atribution of variable \"" + varName + "\"")

            else:
                value["size"] = self.valueSize
                value["keys"] = self.valueKeys
                value["state"][1] = True

            self.valueDataType = None # Useless but for bug-free programming
            self.valueSize = 0 # Useless but for bug-free programming
            self.valueKeys = []

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

    def grammar__declarations__set(self,tree):
        #print("set")
        self.valueDataType = 'set'
        return f"{{{self.visit(tree.children[0])}}}"

    def grammar__declarations__list(self,tree):
        #print("list")
        self.valueDataType = 'list'
        return f"[{self.visit(tree.children[0])}]"

    def grammar__declarations__tuple(self,tree):
        #print("tuple")
        self.valueDataType = 'tuple'
        return f"({self.visit(tree.children[0])})"

    def grammar__declarations__dict(self,tree):
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

        elemList = []
        for key,value in zip(tree.children[0::2], tree.children[1::2]):
            v_key = self.visit(key)
            keyDataType.add(self.valueDataType)
            v_value = self.visit(value)
            valueDataType.add(self.valueDataType)

            if v_key in self.valueKeys:
                repetitiveKeys = True
                break

            self.valueKeys.append(v_key)

            elemList.append(f"{v_key}:{v_value}")

        if repetitiveKeys:
            self.valueDataType = None
            return utils.generateErrorTag(",".join(elemList),"Dictionary has repeated key")

        self.valueSize = len(elemList)

        if len(valueDataType) > 1 or len(keyDataType) > 1:
            self.valueDataType = None
            return utils.generateErrorTag(",".join(elemList),"Data types of dictionary are not uniform")

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
            self.errors.append("Undeclared variable \"" + varName + "\"")
            varName = utils.generateErrorTag(varName,"Undeclared variable")

            self.valueDataType = ''
            self.valueSize = 0

            return varName

        value = self.variables[varName]

        if value["state"] == ""

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
    
