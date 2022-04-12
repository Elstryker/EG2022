from lark.visitors import Interpreter
from lark import Tree,Token
import utils
import re

global identLevel

identLevel = 4

class MainInterpreter (Interpreter):

    def __init__(self):
        self.variables = dict() # var -> {state -> (declared, assigned, used), size -> int, datatype -> str, type -> str, keys -> list}
        self.warnings = []
        self.errors = []
        self.valueType = None
        self.valueDataType = None
        self.valueSize = 1

    def start(self,tree):
        # Visita todos os filhos em que cada um vão retornar o seu código
        res = self.visit_children(tree)

        output = dict()
        # Juntar o código dos vários blocos
        output["html"] = res
        output["vars"] = self.variables
        output["warnings"] = self.warnings
        output["errors"] = self.errors

        return output

    def declaration(self,tree):
        r = self.visit(tree.children[0])
        return r

    def grammar__declarations__atomic_declaration(self,tree):
        print("atomic_decl_init")
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
        print("set_declaration")
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
        print("list_declaration")
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
        print("tuple_declaration")
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
        print("dict_declaration")
        return self.visit_children(tree)

    def grammar__declarations__var(self,tree):
        print("var")
        return str(tree.children[0])

    def grammar__declarations__set(self,tree):
        print("set")
        return self.visit(tree.children[0])

    def grammar__declarations__list(self,tree):
        print("list")
        return self.visit(tree.children[0])

    def grammar__declarations__tuple(self,tree):
        print("tuple")
        return self.visit(tree.children[0])

    def grammar__declarations__dict(self,tree):
        print("dict")
        return self.visit(tree.children[0])

    def grammar__declarations__list_contents(self,tree):
        print("list_contents")
        return self.visit(tree.children[0])

    def grammar__declarations__int_contents(self,tree):
        print("int_contents")
        self.valueDataType = 'int'
        self.valueSize = len(tree.children)
        elemList = []
        for child in tree.children:
            elemList.append(str(child))
        return ",".join(elemList)

    def grammar__declarations__float_contents(self,tree):
        print("float_contents")
        self.valueDataType = 'float'
        self.valueSize = len(tree.children)
        elemList = []
        for child in tree.children:
            elemList.append(str(child))
        return ",".join(elemList)

    def grammar__declarations__string_contents(self,tree):
        print("string_contents")
        self.valueDataType = 'str'
        self.valueSize = len(tree.children)
        elemList = []
        for child in tree.children:
            elemList.append(str(child))
        return ",".join(elemList)

    def grammar__declarations__bool_contents(self,tree):
        print("bool_contents")
        self.valueDataType = 'bool'
        self.valueSize = len(tree.children)
        elemList = []
        for child in tree.children:
            elemList.append(str(child))
        return ",".join(elemList)

    def grammar__declarations__dict_contents(self,tree): #TODO
        print("dict_contents")
        return self.visit_children(tree)

    def grammar__declarations__operand_value(self,tree):
        print("operand_value")
        return self.visit(tree.children[0])

    def grammar__declarations__operand_var(self,tree): #TODO
        print("operand_var")
        return self.visit_children(tree)

    def grammar__declarations__value_string(self,tree):
        print("value_string")
        self.valueType = "atomic"
        self.valueDataType = "str"
        return str(tree.children[0])

    def grammar__declarations__value_float(self,tree):
        print("value_float")
        self.valueType = "atomic"
        self.valueDataType = "float"
        return str(tree.children[0])

    def grammar__declarations__value_int(self,tree):
        print("value_int")
        self.valueType = "atomic"
        self.valueDataType = "int"
        return str(tree.children[0])

    def grammar__declarations__value_bool(self,tree):
        print("value_bool")
        self.valueType = "atomic"
        self.valueDataType = 'bool'
        return str(tree.children[0])
    
    