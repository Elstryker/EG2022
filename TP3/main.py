from lark import Discard
from lark import Lark,Token,Tree
from lark.tree import pydot__tree_to_png

from grammar.grammar import grammar
from interpreter.interpreter import MainInterpreter
from interpreter.interpreterCFG import MainInterpreterCFG
from interpreter.interpreterSDG import MainInterpreterSDG
import interpreter.utils as utils
phrase = """
str a = "1";

str lol = 5;

if(False && 1 < 2) {
    if(z < a) {
        lol = 2;
        lol = 3;
        lol = 4;
    }
    else{
        lol=5;
    }
}
else {
    lol = 7;
    lol = 8;
}

for(lol = 0; False; lol = lol + 1) {
    lol = 4;
    lol = 5;
}
while(1>2 || 3>4 || ze<xico){
    sera=1;
}

"""

"""
"""

p = Lark(grammar)

parse_tree = p.parse(phrase)
cfg = MainInterpreterCFG().visit(parse_tree)
sdg = MainInterpreterSDG().visit(parse_tree)
data = MainInterpreter().visit(parse_tree)

utils.insertGraphsHTML("index.html",sdg["nodes"],sdg["edges"])
