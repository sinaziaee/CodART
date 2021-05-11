from antlr4 import *
from antlr4.TokenStreamRewriter import TokenStreamRewriter

from gen.javaLabeled.JavaParserLabeled import JavaParserLabeled
from gen.javaLabeled.JavaLexer import JavaLexer
from gen.javaLabeled.JavaParserLabeledListener import JavaParserLabeledListener
import os
try:
    import understand as und
except ImportError as e:
    print(e)

class ExtractMethodRefactoring(JavaParserLabeledListener):

    def __init__(self, common_token_stream: CommonTokenStream = None,
                 target_class: str = None):
        # self.enter_class = False
        self.token_stream = common_token_stream
        self.class_identifier = target_class
        # Move all the tokens in the source code in a buffer, token_stream_rewriter.
        if common_token_stream is not None:
            self.token_stream_rewriter = TokenStreamRewriter(common_token_stream)
        else:
            raise TypeError("common_token_stream is None")
        self.field_dict = {}
        self.method_name = []  #
        self.method_no = 0
        self.connected_components = []


def main(udb_path, target_class):
    print("Make Method Static")
    main_file = ""
    db = open(udb_path)
    for cls in db.ents("class"):
        if cls.simplename() == source_class:
            main_file = cls.parent().longname(True)
            if not os.path.isfile(main_file):
                continue
    if main_file is None:
        return

    stream = FileStream(main_file, encoding='utf8')
    lexer = JavaLexer(stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParserLabeled(token_stream)
    parser.getTokenStream()
    parse_tree = parser.compilationUnit()
    my_listener = ExtractMethodRefactoring(common_token_stream=token_stream,
                                           target_class=target_class
                                           )
    walker = ParseTreeWalker()
    walker.walk(t=parse_tree, listener=my_listener)

    with open(main_file, mode='w', newline='') as f:
        f.write(my_listener.token_stream_rewriter.getDefaultText())


if __name__ == '__main__':
    test_path = "/home/ali/Desktop/code/TestProject/TestProject.udb"
    source_class = "Test"
    main(test_path, source_class)
