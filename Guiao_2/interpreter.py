from lark.visitors import Interpreter
from lark import Tree,Token

class MyInterpreter (Interpreter):

    def __init__(self):
        self.variables = dict()  # Mapping from varname to a tuple -> (Declared,Assigned,Used)
        self.warnings = []
        self.errors = []
    
    def start(self,tree):
        r = []
        for child in tree.children:
            r += self.visit(child)

        print("Variables: ", self.variables)

        return "\n".join(r) 
    
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
            if tree.children[3].children[0].data == "var":
                if value in self.variables:
                    self.variables[value][2] = True
                else:
                    self.variables[value] = [False,False,True]

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
        return self.visit(tree.children[0])

    def atribution(self,tree):
        varName = self.visit(tree.children[0])

        if varName in self.variables:
            self.variables[varName][1] = True
        else:
            self.variables[varName] = [False,True,False]

        value = self.visit(tree.children[2])

        if tree.children[2].children[0].data == "var":
            if value in self.variables:
                self.variables[value][2] = True
            else:
                self.variables[value] = [False,False,True]

        return f"{varName} = {value};"


    def condition(self,tree):
        boolexpr = self.visit(tree.children[1])

        codeTrue = self.visit(tree.children[3])

        codeFalse = ''

        if len(tree.children) > 5:
            codeFalse = self.visit(tree.children[7])

        codeString = "if" + boolexpr + """ {
    """ + "\n    ".join(codeTrue) + """
}"""

        if codeFalse != '':
            codeString += """
else {
    """ + "\n    ".join(codeFalse) + """
}"""

        return codeString

    def boolexpr(self,tree):
        # TODO var logic on self.variables
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
