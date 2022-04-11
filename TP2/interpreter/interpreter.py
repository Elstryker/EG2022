from lark.visitors import Interpreter
from lark import Tree,Token
import re

global identLevel

identLevel = 4

class MainInterpreter (Interpreter):

    def __init__(self):
        pass

    