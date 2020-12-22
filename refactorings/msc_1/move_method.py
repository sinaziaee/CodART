from antlr4_java9.Java9Lexer import Java9Lexer
from antlr4_java9.Java9Parser import Java9Parser
from networkx.algorithms.planarity import Interval
from utils_listener import UtilsListener, Program
from utils_listener import TokensInfo
from utils import get_program,Rewriter
from antlr4 import *
from antlr4_java9.Java9Lexer import Java9Lexer
from utils_listener import UtilsListener, Java9Parser
from utils import get_program



def move_method_refactoring(source_filenames: list, package_name: str, class_name: str, method_name: str,target_class_name : str, filename_mapping = lambda x: x + ".rewritten.java"):
    program = get_program(source_filenames)
    _sourceclass = program.packages[package_name].classes[class_name]
    _targetclass = program.packages[package_name].classes[target_class_name]
    _method =program.packages[package_name].classes[class_name].methods[method_name]
    Rewriter_= Rewriter(program,filename_mapping)
    tokens_info = TokensInfo(_method.parser_context)
    for package_name in program.packages:
     package = program.packages[package_name]
     for class_ in package.classes:
        _class = package.classes[class_]
        for method_ in _class.methods:
            _method = _class.methods[method_]
            i=0
            for inv in _method.body_method_invocations:

                invc = _method.body_method_invocations[i]
                if(invc != None):
                    inv_tokens_info = TokensInfo(invc)
                    Rewriter_.replace(inv_tokens_info,target_class_name)
                    Rewriter_.apply()
                    i=i+1





    class_tokens_info = TokensInfo(_targetclass.parser_context)
    Rewriter_.insert_before(tokens_info=class_tokens_info,text=_method.parser_context.getText())
    Rewriter_.replace(tokens_info,"")
    Rewriter_.apply()
    print(_sourceclass)
    print(_targetclass)
    print(_method)
    print(_method.parser_context.start)
    print(_method.parser_context.stop)
mylist = ["tests/Test.java","tests/sourceclass.java","tests/targetclass.java"]
move_method_refactoring(mylist,"tests.utils_test2","sourceclass","d","targetclass")


