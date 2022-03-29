from lark.visitors import Interpreter
from lark import Tree,Token

global identLevel

identLevel = 4

def detectWarningsAndErrors(vars : dict):
    errors = []
    warnings = []

    for var,(decl,assigned,used) in vars.items():
        if decl and used and not assigned:
            errors.append(f'Variable "{var}" attempted to be used but not assigned')
        elif decl and not assigned:
            warnings.append(f'Variable "{var}" declared but not assigned')
        if decl and not used and assigned:
            warnings.append(f'Variable "{var}" declared but not used')
        if used and not decl:
            errors.append(f'Undeclared variable "{var}" attempted to be used')
        if assigned and not decl:
            errors.append(f'Undeclared variable "{var}" attempted to be assigned')

    return (warnings, errors)


class MyInterpreter (Interpreter):

    def __init__(self):
        self.variables = dict()  # Mapping from varname to a tuple -> (Declared,Assigned,Used)
        self.numberIfs = 0
        self.ifDepth = 0
        self.maxIfDepth = 0
    
    def start(self,tree):
        r = []
        for child in tree.children:
            r += self.visit(child)

        print("Variables: ", self.variables)

        (warnings, errors) = detectWarningsAndErrors(self.variables)

        output = dict()
        output["code"] = "\n".join(r)
        output["numberIfs"] = self.numberIfs
        output["warnings"] = warnings
        output["errors"] = errors
        output["maxIfDepth"] = self.maxIfDepth

        return output
    
    def initializations(self,tree):
        r = []
        for child in tree.children:
            if isinstance(child,Tree):
                r.append(self.visit(child))

        return r

    def initialization(self,tree):
        childNum = len(tree.children)

        type = str(tree.children[0])

        varName = self.visit(tree.children[1])
        if varName not in self.variables:
            self.variables[varName] = [True,False,False]  # Declared, Assigned, Used
        else:
            self.variables[varName][0] = True

        code = f"{type} {varName}"

        if childNum > 2:
            value = self.visit(tree.children[3])

            code += f" = {value}"

            self.variables[varName][1] = True

        code += ";"

        return code


    def var(self,tree):
        return str(tree.children[0])

    def code(self,tree):
        r = list()
        for child in tree.children:
            r.append(self.visit(child))

        return r

    def block(self,tree):
        return self.visit(tree.children[0])

    def value(self,tree):
        return str(tree.children[0])

    def operand(self,tree):
        value = self.visit(tree.children[0])
        if tree.children[0].data == 'var':
            if value in self.variables:
                self.variables[value][2] = True
            else:
                self.variables[value] = [False,False,True]

        return value

    def atribution(self,tree):
        varName = self.visit(tree.children[0])

        if varName in self.variables:
            self.variables[varName][1] = True
        else:
            self.variables[varName] = [False,True,False]

        value = self.visit(tree.children[2])

        return f"{varName} = {value};"


    def condition(self,tree):
        self.numberIfs += 1
        ifDepth = self.ifDepth
        self.ifDepth += 1
        self.maxIfDepth = self.maxIfDepth if self.maxIfDepth > ifDepth else ifDepth

        boolexpr = self.visit(tree.children[1])

        codeTrue = self.visit(tree.children[3])

        codeFalse = ''

        ident = ((ifDepth + 1) * identLevel * " ")
        lastIdent = (ifDepth * identLevel * " ")

        if len(tree.children) > 5:
            codeFalse = self.visit(tree.children[7])

        codeString = "if" + boolexpr + """ { // level """ + str(ifDepth) + "\n" + ident + ("\n"+ident).join(codeTrue) + "\n" + lastIdent + "}"
        
        if codeFalse != '':
            codeString += "\n"+ lastIdent + "else { // level " + str(ifDepth) + "\n" + ident + ("\n"+ident).join(codeFalse) + "\n" + lastIdent + "}"

        self.ifDepth = ifDepth

        return codeString

    def boolexpr(self,tree):
        operand1 = self.visit(tree.children[1])
        operator = self.visit(tree.children[2])
        operand2 = self.visit(tree.children[3])

        return f"({operand1} {operator} {operand2})"

    def operator(self,tree):
        return str(tree.children[0])

    def cycle(self,tree):
        boolexp = self.visit(tree.children[1])

        code = self.visit(tree.children[3])

        codeString = "while" + boolexp + """ {
    """ + "\n    ".join(code) + """
}"""

        return codeString
