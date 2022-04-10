from lark.visitors import Interpreter
from lark import Tree,Token
import re

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
        self.canReplace = dict()
        self.numberIfs = 0
        self.ifDepth = 0
        self.maxIfDepth = 0
        self.numberCycles = 0
        self.cycleDepth = 0
        self.maxCycleDepth = 0
    
    def start(self,tree):
        r = []
        # Visita todos os filhos em que cada um vão retornar o seu código
        for child in tree.children:
            r += self.visit(child)

        print("Variables: ", self.variables)

        (warnings, errors) = detectWarningsAndErrors(self.variables)

        output = dict()
        # Juntar o código dos vários blocos
        output["code"] = "\n".join(r)
        output["numberIfs"] = self.numberIfs
        output["warnings"] = warnings
        output["errors"] = errors
        output["maxIfDepth"] = self.maxIfDepth
        output["maxCycleDepth"] = self.maxCycleDepth
        output["numberCycles"]=self.numberCycles

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

        if(ind:=re.search(r'\[\d+\]',varName)):
            varName=re.sub(ind.group(0),"",varName)
            varName=re.sub(r'\[\]',"",varName)

        # Atualiza a estrutura com o estado das variáveis
        if varName not in self.variables:
            if ind:
                index= re.sub(r'\[',"",ind.group(0))
                index= re.sub(r'\]',"",index)
                i=0
                for i in range(int(index)):
                    self.variables[varName+"["+str(i)+"]"] = [True,False,False]
            else:
                self.variables[varName] = [True,False,False]  # Declared, Assigned, Used
        else:
            self.variables[varName][0] = True

        if ind:
            code = f"{type} {varName}{ind.group(0)}"
        else:
            code = f"{type} {varName}"
        # Caso a declaração tenha inicialização, processa-a
        if childNum > 2:
            if varName not in self.variables:
                if ind:
                    index= re.sub(r'\[',"",ind.group(0))
                    index= re.sub(r'\]',"",index)
                    i=0
                    while i <= int(index):
                        self.variables[varName+"["+str(i)+"]"] = [True,False,False]
                        i+=1
                else:
                    self.variables[varName] = [True,False,False]  # Declared, Assigned, Used
            else:
                self.variables[varName][0] = True

            if not ind:
                value = self.visit(tree.children[3])

                code += f" = {value}"

                self.variables[varName][1] = True
            else:
                value =self.visit(tree.children[3])
                code += f" = {value}"

                self.variables[varName+ind.group(0)][1] = True

        code += ";"

        return code


    def var(self,tree):
        ret =""
        for elem in tree.children:
            ret+=str(elem)
        return ret

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

        return value

    def atribution(self,tree):
        ret=""

        for i,item in enumerate(tree.children):
            if i==0:
                item = self.visit(tree.children[0])

                if item in self.variables:
                    self.variables[item][1]=True
                else:
                    self.variables[item] = [False,True,False]
                
                ret += f'{item} '

            elif not ((i % 2)==0):
                if i>=3:
                    item = self.visit(tree.children[i])
                    ret += f'{item} '
                else:
                    ret += f'{item} '
                
            elif (i % 2) ==0:
                item = self.visit(tree.children[i])
                ret += f"{item} "
        
        return ret


    def condition(self,tree):
        self.numberIfs += 1
        # Variável local para guardar o seu nível

        ifDepth = self.ifDepth
        self.ifDepth += 1
        self.maxIfDepth = self.maxIfDepth if self.maxIfDepth > ifDepth else ifDepth

        boolexpr = self.visit(tree.children[1])
        codeTrue = self.visit(tree.children[3])
        catchBool = re.match(r'(if)(\(.*\)\s*){',codeTrue[0])
       

        if(catchBool and len(tree.children)<6):
            for k in self.canReplace:
                if(k in catchBool.group(2)):
                    boolexpr = re.sub(r"\)","",boolexpr)
                    sub = re.sub(r"\(","",catchBool.group(2))
                    sub = re.sub(r"\)","",sub)
                    boolexpr += "&&" + sub + ")"
                    codeTrue[0]= codeTrue[0].replace(catchBool.group(0),"")
                    codeTrue[0]= re.sub(r"^.*[\n]","",codeTrue[0])
                    idx = codeTrue[0].rfind("}")
                    if(idx>=0):
                        codeTrue[0]=codeTrue[0][:idx]
                    

                    
                    
        elseContent = ''

        if len(tree.children)<6:
            self.canReplace[boolexpr]=[codeTrue]
        
        else:
            elseContent=self.visit(tree.children[5])

       
        
            

        # Cálculo da identação para pretty printing
        ident = ((ifDepth + 1) * identLevel * " ")
        lastIdent = (ifDepth * identLevel * " ")


        codeString = "if" + boolexpr + """ { // level """ + str(ifDepth) + "\n" + ident + ("\n"+ident).join(codeTrue) + "\n" + lastIdent + "}"
        
        # Processamento de else se houver
        if elseContent != '':
            codeString += "\n"+ lastIdent + "else { // level " + str(ifDepth) + "\n" + ident + ("\n"+ident).join(elseContent) + "\n" + lastIdent + "}"

        self.ifDepth = ifDepth

        return codeString

    def boolexpr(self,tree):
        ret = ""
        if(len(tree.children)<=3):
            op = tree.children[0]
            operand = self.visit(tree.children[1])
            cp = tree.children[2]
            ret += f"{op} {operand} {cp}"
        else:
            for i,item in enumerate(tree.children):
                if i>0 and not((i%4)==0):
                    item = self.visit(tree.children[i])
                    ret += f"{item} "
                else:
                    ret += f"{item} "

        return ret


    def elsecond (self,tree):
        return self.visit(tree.children[2])

    def operator(self,tree):
        return str(tree.children[0])

    def cycle(self,tree):
        self.numberCycles += 1

        cycleDepth = self.cycleDepth
        self.cycleDepth +=1
        self.maxCycleDepth = self.maxCycleDepth if self.maxCycleDepth > cycleDepth else cycleDepth


        boolexp = self.visit(tree.children[1])

        code = self.visit(tree.children[3])


        # Cálculo da identação para pretty printing
        ident = ((cycleDepth + 1) * identLevel * " ")
        lastIdent = ( cycleDepth * identLevel * " ")


        codeString = "while" + boolexp + """ { // level """ + str(cycleDepth) + "\n" + ident + ("\n"+ident).join(code) + "\n" + lastIdent + "}"

        self.cycleDepth = cycleDepth
        return codeString
