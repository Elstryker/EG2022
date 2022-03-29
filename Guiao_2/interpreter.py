from lark.visitors import Interpreter
from lark import Tree,Token

class MyInterpreter (Interpreter):

    def __init__(self):
        self.variables = dict()  # Mapping from varname to a tuple -> (Declared,Assigned,Used)
    
    def start(self,tree):
        r = []
        for child in tree.children:
            r.append(self.visit(child))

        return r 
    
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

    # def code(self,tree):
    #     pass

    # def block(self,tree):
    #     pass

    def value(self,tree):
        return str(tree.children[0])

    # def atribution(self,tree):
    #     pass

    # def condition(self,tree):
    #     pass

    # def boolexpr(self,tree):
    #     pass

    # def operator(self,tree):
    #     pass

    # def operand(self,tree):
    #     pass

    # def cycle(self,tree):
    #     pass
