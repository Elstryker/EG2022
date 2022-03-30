from lark.visitors import Interpreter
from lark import Tree,Token
import utils

global identNumber

identNumber = 4


class MyInterpreter (Interpreter):

    def __init__(self):
        self.variables = dict()  # Mapping from varname to a tuple -> (Declared,Assigned,Used)
        self.identLevel = 0
        self.numberIfs = 0
        self.ifDepth = 0
        self.maxIfDepth = 0
    
    def start(self,tree):
        res = []
        # Visita todos os filhos em que cada um vão retornar o seu código
        for child in tree.children:
            res += self.visit(child)

        print("Variables: ", self.variables)

        utils.generateHTML(''.join(res))

        output = dict()
        # Juntar o código dos vários blocos
        output["html"] = ''.join(res)

        return output
    
    def initializations(self,tree):
        r = []
        # Busca do código das inicializações
        for child in tree.children:
            if isinstance(child,Tree):
                r.append(self.visit(child))

        return r

    def initialization(self,tree):
        childNum = len(tree.children)

        type = str(tree.children[0])

        varName = self.visit(tree.children[1])
        # Atualiza a estrutura com o estado das variáveis
        if varName not in self.variables:
            self.variables[varName] = [True,False,False]  # Declared, Assigned, Used
        else:
            self.variables[varName][0] = True

        code = f"{type} {varName}"
        # Caso a declaração tenha inicialização, processa-a
        if childNum > 2:
            value = self.visit(tree.children[3])

            code += f" = {value}"

            self.variables[varName][1] = True

        code += ";"

        return utils.generatePClassCodeTag(code)


    def var(self,tree):
        return str(tree.children[0])

    def code(self,tree):
        r = list()
        # Busca do código das inicializações
        for child in tree.children:
            r.append(self.visit(child))

        return r

    def block(self,tree):
        return self.visit(tree.children[0])

    def value(self,tree):
        return str(tree.children[0])

    def operand(self,tree):
        value = self.visit(tree.children[0])
        # Atualização do estado da variável na estrutura de dados caso o operando seja variavel
        if tree.children[0].data == 'var':
            if value in self.variables:
                self.variables[value][2] = True
            else:
                self.variables[value] = [False,False,True]

            if self.variables[value][1] == False or self.variables[value][0] == False:
                return utils.generateNonInitializedErrorTag(value)


        return value

    def atribution(self,tree):
        varName = self.visit(tree.children[0])

        value = self.visit(tree.children[2])

        ident = (self.identLevel * identNumber * " ")

        # Atualização do estado da variável na estrutura de dados
        if varName in self.variables:
            self.variables[varName][1] = True
        else:
            self.variables[varName] = [False,True,False]
            utils.generateNonInitializedErrorTag(value)


        if self.variables[varName][1] == False or self.variables[varName][0] == False:
            codeStr = f"{utils.generateNonInitializedErrorTag(varName)} = {value};"
        else:
            codeStr = f"{varName} = {value};"

        return utils.generatePClassCodeTag(ident + codeStr)


    def condition(self,tree):
        identDepth = self.identLevel
        ifDepth = self.ifDepth
        self.ifDepth += 1
        self.maxIfDepth = self.maxIfDepth if self.maxIfDepth > ifDepth else ifDepth


        self.identLevel += 1
        self.numberIfs += 1


        boolexpr = self.visit(tree.children[1])

        codeTrue = self.visit(tree.children[3])

        codeFalse = ''

        # Cálculo da identação para pretty printing
        ident = (identDepth * identNumber * " ")

        if len(tree.children) > 5:
            codeFalse = self.visit(tree.children[7])

        taggedCode = utils.generatePClassCodeTag(ident + "if" + boolexpr + " { // ifLevel: " + str(ifDepth))
        taggedCode += ''.join(codeTrue)
        taggedCode += utils.generatePClassCodeTag(ident + '}')
        
        # Processamento de else se houver
        if codeFalse != '':
            taggedCode += utils.generatePClassCodeTag(ident + 'else { // ifLevel: ' + str(ifDepth))
            taggedCode += ''.join(codeFalse)
            taggedCode += utils.generatePClassCodeTag(ident + '}')

        self.identLevel = identDepth
        self.ifDepth = ifDepth

        return taggedCode

    def boolexpr(self,tree):
        operand1 = self.visit(tree.children[1])
        operator = self.visit(tree.children[2])
        operand2 = self.visit(tree.children[3])

        return f"({operand1} {operator} {operand2})"

    def operator(self,tree):
        return str(tree.children[0])

    def cycle(self,tree):
        identDepth = self.identLevel
        self.identLevel += 1

        # Cálculo da identação para pretty printing
        ident = (identDepth * identNumber * " ")

        boolexp = self.visit(tree.children[1])

        code = self.visit(tree.children[3])

        taggedCode = utils.generatePClassCodeTag(ident + "while" + boolexp + " {")
        taggedCode += ''.join(code)
        taggedCode += utils.generatePClassCodeTag(ident + "}")

        self.identLevel = identDepth

        return taggedCode
