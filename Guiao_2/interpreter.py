from lark.visitors import Interpreter

class MyInterpreter (Interpreter):

    def __init__(self):
        self.variables = dict()
    
    def start(self,tree):
        pass
    
    def initializations(self,tree):
        pass

    def initialization(self,tree):
        pass

    def var(self,tree):
        pass

    def code(self,tree):
        pass

    def block(self,tree):
        pass

    def value(self,tree):
        pass

    def atribution(self,tree):
        pass

    def condition(self,tree):
        pass

    def boolexpr(self,tree):
        pass

    def operator(self,tree):
        pass

    def operand(self,tree):
        pass

    def cycle(self,tree):
        pass
