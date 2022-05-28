from distutils.log import error
from lark.visitors import Interpreter
from lark import Tree,Token
import interpreter.utils as utils
import re, graphviz

global identNumber

identNumber = 4


visitedList = [[]]

def depthFirst(graph, currentVertex, visited):
    visited.append(currentVertex)
    for vertex in graph[currentVertex]:
        if vertex not in visited:
            depthFirst(graph, vertex, visited.copy())
    if(len(visited)>1):
        visitedList.append(visited)

def checkVars(elems):
    hasVars=False
    for elem in elems:
        if not hasVars and elem.isalpha() and not(elem.lower()=="False".lower()) and not(elem.lower()=="True".lower()):
            hasVars=True
    return hasVars

def createGraph(graph, graphMap,unreach):
    dot = graphviz.Digraph('System Dependency Graph',strict=True)
    
    for (beg,currentVertex) in unreach:
            depthFirst(graph,currentVertex,[])
    auxVisited = visitedList
    for i,node in enumerate(graph):
        dot.node(str(i),graphMap[i])
        for arrs in auxVisited:
            if len(arrs)>0:
                arrs = arrs[1:]
                for i in range(len(arrs)-1):
                    frm = arrs[i]
                    to = arrs[i+1]
                    dot.edge(str(frm),str(to),color="red")
        auxVisited=[]
        for row in node:
            for idx,(beg,end) in enumerate(unreach):
                if(i==beg and row == end):
                    dot.edge(str(i),str(row),color="red")
                elif(i==end):
                    dot.edge(str(i),str(row),color="red")
                

            dot.edge(str(i),str(row))
                
    dot.render("System Dependency Graph.gv",view=True)

    return dot


def checkUnreachable(graph,graphMap):
    aux = []
    opDel = ">|<|>=|<=|!=|=="
    for k in graphMap:
        
        if("for " in graphMap[k] or "if " in graphMap[k] or "do_while " in graphMap[k] or
            "while " in graphMap[k]):
            hasVars = False
            conditions =[]
            exp = graphMap[k]
            exp = exp.strip()
            fullExp = exp.split(' ', 1)[1]
            cond = exp.split(" ")
            func = cond[0]
            for elems in cond[1:]:
                elems = elems.strip()
                elems= elems.split(" ")

                hasVars = checkVars(cond[1:])
                
            conditions = [ele for ele in conditions if ele.strip()]
            if hasVars:
                sepAnd = False
                sepOr = False
                if "&&" in fullExp:
                    sepAnd = True
                elif "||" in fullExp:
                    sepOr=True
                if sepAnd:
                    expToEval = fullExp.split("&&")
                    count=0
                    for exp in expToEval:
                        insideVars = checkVars(exp)
                        if(not insideVars and eval(exp)==False):
                            count+=1
                    if func=="if" and count>0:
                        if(len(graph[k])>1):
                            aux.append((k,graph[k][-1]))
                    elif count>0:
                        if func=="if":
                            aux.append((k,graph[k][0]))
                        else:
                            for x in graph[k]:
                                aux.append((k,x))
                elif sepOr:
                    expToEval = fullExp.split("||")
                    count=0
                    for exp in expToEval:
                        insideVars = checkVars(exp)
                        if(not insideVars and eval(exp)==True):
                            count+=1
                    if func=="if" and count>0:
                        if(len(graph[k])>1):
                            aux.append((k,graph[k][-1]))
                    elif count>0:
                        if func=="if":
                            aux.append((k,graph[k][0]))
                        else:
                            for x in graph[k]:
                                aux.append((k,x))

            if not hasVars:
                expToEval = fullExp.replace("&&","and")
                expToEval = expToEval.replace("||","or")
                value= eval(expToEval)
                if func=="if" and value:
                    if(len(graph[k])>1):
                        aux.append((k,graph[k][-1]))
                elif not value:
                    if func=="if":
                        aux.append((k,graph[k][0]))
                    else:
                        for x in graph[k]:
                            aux.append((k,x))
    return aux

def mccabeComplexity(graph,graphMap):
    numberNodes = len(graphMap)
    numberEdges = 0
    for conj in graph:
        numberEdges+=len(conj)
    return numberEdges-numberNodes+2


class MainInterpreterSDG (Interpreter):

    def __init__(self):
        self.graph = []
        self.graphMap = {}
        self.nodeBefore = None
        self.nodeCount = 0
        self.graphNext = False
        self.connectParent = list()

    def start(self,tree):
        # Visita todos os filhos em que cada um vão retornar o seu código
        self.graph.append(list())
        self.graphMap[0] = 'entry main'
        self.nodeCount = 1
        self.connectParent.append(0)

        res = self.visit_children(tree)

        print(self.graph)
        print(self.graphMap)
        unreach = checkUnreachable(self.graph,self.graphMap)
        #complexity = mccabeComplexity(self.graph,self.graphMap)
        
        graph = createGraph(self.graph, self.graphMap,unreach)
        graph.save()
        graphviz.render('dot','png','System Dependency Graph.gv')
        #print(graph)
        
        output = dict()
        # Juntar o código dos vários blocos
        output["html"] = res[0]
        output["vars"] = self.variables
        output["graph"] = graph
        


        return output

    def declaration(self,tree):
        r = self.visit(tree.children[0])
        return r

    def __generalDeclarationVisitor(self,tree,type):
        dataType = str(tree.children[0])
        varName = self.visit(tree.children[1])
        childNum = len(tree.children)

        self.graph.append(list())

        self.graph[self.connectParent[-1]].append(self.nodeCount)
                
        # if variable is assigned
        if childNum > 2:
            operand = self.visit(tree.children[2])

            self.graphMap[self.nodeCount] = f"{dataType}{'' if type == 'atomic' else ' ' + type} {varName} = {operand}"

            code = f"{dataType}{'' if type == 'atomic' else ' ' + type} {varName} = {operand};"

        else:

            self.graphMap[self.nodeCount] = f"{dataType}{'' if type == 'atomic' else ' ' + type} {varName}"

            code = f"{dataType}{'' if type == 'atomic' else ' ' + type} {varName};"

        self.nodeCount += 1

        return code

    def grammar__declarations__atomic_declaration(self,tree):
        return self.__generalDeclarationVisitor(tree,"atomic")

    def grammar__declarations__set_declaration(self,tree):
        return self.__generalDeclarationVisitor(tree,"set")

    def grammar__declarations__list_declaration(self,tree):
        return self.__generalDeclarationVisitor(tree,"list")

    def grammar__declarations__tuple_declaration(self,tree):
        return self.__generalDeclarationVisitor(tree,"tuple")

    def grammar__declarations__dict_declaration(self,tree):
        keyDataType = str(tree.children[0])
        valueDataType = str(tree.children[1])
        varName = self.visit(tree.children[2])
        childNum = len(tree.children)

        self.graph.append(list())
        
        self.graph[self.connectParent[-1]].append(self.nodeCount)
                
        # if variable is assigned
        if childNum > 3:
            # Get value assigned to
            operand = self.visit(tree.children[3])

            self.graphMap[self.nodeCount] = f"({keyDataType},{valueDataType}) dict {varName} = {operand}"

            code = f"({keyDataType},{valueDataType}) dict {varName} = {operand};"

        else:

            self.graphMap[self.nodeCount] = f"({keyDataType},{valueDataType}) dict {varName}"

            code = f"({keyDataType},{valueDataType}) dict {varName};"

        self.nodeCount += 1

        return code

    def grammar__declarations__var(self,tree):
        return str(tree.children[0])

    def set(self,tree):
        return f"{{{self.visit(tree.children[0])}}}"

    def list(self,tree):
        return f"[{self.visit(tree.children[0])}]"

    def tuple(self,tree):
        return f"({self.visit(tree.children[0])})"

    def dict(self,tree):
        return f"{{{self.visit(tree.children[0])}}}"

    def grammar__declarations__list_contents(self,tree):
        return self.visit(tree.children[0])

    def grammar__declarations__int_contents(self,tree):
        elemList = []
        for child in tree.children:
            elemList.append(str(child))
        return ",".join(elemList)

    def grammar__declarations__float_contents(self,tree):
        elemList = []
        for child in tree.children:
            elemList.append(str(child))
        return ",".join(elemList)

    def grammar__declarations__string_contents(self,tree):
        elemList = []
        for child in tree.children:
            elemList.append(str(child))
        return ",".join(elemList)

    def grammar__declarations__bool_contents(self,tree):
        elemList = []
        for child in tree.children:
            elemList.append(str(child))
        return ",".join(elemList)

    def grammar__declarations__dict_contents(self,tree):
        elemList = []

        for key,value in zip(tree.children[0::2], tree.children[1::2]):
            v_key = self.visit(key)
            v_value = self.visit(value)
            
            elemList.append(f"{v_key}:{v_value}")

        return ",".join(elemList)

    def grammar__declarations__dict_value(self,tree):
        return self.visit(tree.children[0])

    def grammar__declarations__operand_value(self,tree):
        return self.visit(tree.children[0])

    def grammar__declarations__operand_var(self,tree):
        varName = self.visit(tree.children[0])
        return varName

    def grammar__declarations__value_string(self,tree):
        return str(tree.children[0])

    def grammar__declarations__value_float(self,tree):
        return str(tree.children[0])

    def grammar__declarations__value_int(self,tree):
        return str(tree.children[0])

    def grammar__declarations__value_bool(self,tree):
        return str(tree.children[0])
    
    def code(self,tree):
        r=list()
        for child in tree.children:
            r.append(self.visit(child))
        return r

    def instruction(self,tree):
        return self.visit(tree.children[0])

    def atribution(self,tree):
        varName = self.visit(tree.children[0])

        exp = self.visit(tree.children[1])

        self.graph.append(list())
        
        self.graph[self.connectParent[-1]].append(self.nodeCount)

        self.graphMap[self.nodeCount] = f"{varName} = {exp}"

        self.nodeCount += 1

        atrStr = f"{varName} = {exp};"
        
        return atrStr


    def condition(self,tree):
        cond = self.visit(tree.children[0])

        self.graph.append(list())

        self.graph[self.connectParent[-1]].append(self.nodeCount)

        self.graphMap[self.nodeCount] = "if "+cond

        ifNodeCount = self.nodeCount

        self.nodeCount += 1

        self.graph.append(list())
        self.graph[ifNodeCount].append(self.nodeCount)
        self.graphMap[self.nodeCount] = "then"
        self.connectParent.append(self.nodeCount)

        self.nodeCount += 1

        code = self.visit(tree.children[1])

        self.connectParent.pop()

        taggedCode = "if("+cond+") {"
        taggedCode += ''.join(code)
        taggedCode += "}"

        return taggedCode

    def condition_else(self,tree):
        cond = self.visit(tree.children[0])

        self.graph.append(list())

        self.graph[self.connectParent[-1]].append(self.nodeCount)
        self.graphMap[self.nodeCount] = "if "+cond

        ifNodeCount = self.nodeCount

        self.nodeCount += 1

        self.graph.append(list())
        self.graph[ifNodeCount].append(self.nodeCount)
        self.graphMap[self.nodeCount] = "then"
        self.connectParent.append(self.nodeCount)

        self.nodeCount += 1

        code = self.visit(tree.children[1])

        self.connectParent.pop()

        self.graph.append(list())
        self.graph[ifNodeCount].append(self.nodeCount)
        self.graphMap[self.nodeCount] = "else"
        self.connectParent.append(self.nodeCount)

        self.nodeCount += 1

        elseCode = self.visit(tree.children[2])

        self.connectParent.pop()

        returnCode = ("if( "+cond+") {")
        returnCode += ''.join(code)
        returnCode +=("}")
        returnCode +=("else {")
        returnCode += ''.join(elseCode)
        returnCode +=("}")

        return returnCode

    def cycle(self,tree):
        return self.visit(tree.children[0])

    def while_cycle(self,tree):
        bool=self.visit(tree.children[0])

        self.graph.append(list())
        self.graph[self.connectParent[-1]].append(self.nodeCount)

        self.graphMap[self.nodeCount] = "while "+ bool
        self.connectParent.append(self.nodeCount)

        self.nodeCount += 1

        code=self.visit(tree.children[1])

        self.connectParent.pop()


        returnCode = "while(" + bool + ") {"
        returnCode += ''.join(code)
        returnCode += "}"
    
        return returnCode

    def do_while_cycle(self,tree):

        self.graph.append(list())
        self.graph[self.connectParent[-1]].append(self.nodeCount)

        bool=self.visit(tree.children[1])

        self.graphMap[self.nodeCount] = "do_while " + bool

        self.connectParent.append(self.nodeCount)
        self.nodeCount += 1

        code=self.visit(tree.children[0])

        self.connectParent.pop()

        returnCode = "do {"
        returnCode += ''.join(code)
        returnCode += "} while("+bool+")"

        return returnCode

    def repeat_cycle(self,tree):
        mat=self.visit(tree.children[0])

        self.graph.append(list())
        self.graph[self.connectParent[-1]].append(self.nodeCount)

        self.graphMap[self.nodeCount] = "repeat " + mat

        self.connectParent.append(self.nodeCount)
        self.nodeCount += 1

        code=self.visit(tree.children[1])

        self.connectParent.pop()

        self.nodeCount += 1

        returnCode = "repeat(" + mat + ") {"
        returnCode += ''.join(code)
        returnCode += "}"

        return returnCode
        
    def for_cycle(self,tree):
        self.graph.append(list())
        self.graph[self.connectParent[-1]].append(self.nodeCount)

        childInfo = [None,None,None,None]
        childInfo[1] = self.visit(tree.children[1]) # Condition

        self.graphMap[self.nodeCount] = "for " + childInfo[1]

        self.connectParent.append(self.nodeCount)
        self.nodeCount += 1

        childInfo[0] = self.visit(tree.children[0]) # Atribution 1
        childInfo[3] = self.visit(tree.children[3]) # Code
        childInfo[2] = self.visit(tree.children[2]) # Atribution 2

        self.connectParent.pop()

        insidePar = f'{"" if childInfo[0] is None else childInfo[0]};{"" if childInfo[1] is None else childInfo[1]};{"" if childInfo[2] is None else childInfo[2]}'

        returnCode = "for(" + insidePar + ") {"
        returnCode += ''.join(childInfo[3])
        returnCode += "}"

        print(returnCode)

        return returnCode


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
        r=""
        for child in tree.children:
            if(isinstance(child,Tree)):
                r+=self.visit(child)+" "
            else:
                r+=child+" "
        
        return r


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
        varName = str(tree.children[0])
        retStr = varName

        if(len(tree.children) > 1):
            operand = self.visit(tree.children[1])
            retStr += '[' + operand + ']'

        return retStr
    