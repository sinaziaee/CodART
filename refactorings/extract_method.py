from antlr4 import *
from antlr4.TokenStreamRewriter import TokenStreamRewriter
import datetime
from gen.javaLabeled.JavaParserLabeled import JavaParserLabeled
from gen.javaLabeled.JavaLexer import JavaLexer
from gen.javaLabeled.JavaParserLabeledListener import JavaParserLabeledListener

try:
    import understand as und
except ImportError as e:
    print(e)

"""
    An Extraction method refactoring class for using compiler listeners 
    Authors: Sajjad Naghizadeh, Sadegh Jafari, Sina Ziaee
    
    Description about the code:
    - statements are each line of code showing an act for example a = 5 is an statement.
    - exact each method of each class.
"""


def is_equivalent(a, b):
    if str(a) == str(b):
        return True
    return False


"""
    Extract method factoring class extending java parser labeled listener
"""


class ExtractMethodRefactoring(JavaParserLabeledListener):

    def __init__(self, common_token_stream: CommonTokenStream = None,
                 target_package: str = None, target_class: str = None,
                 target_method: str = None, staring_line: int = 0,
                 ending_line: int = 1, length: int = None):
        # self.enter_class = False
        self.token_stream = common_token_stream
        self.class_identifier = target_class
        # Move all the tokens in the source code in a buffer, token_stream_rewriter.
        if common_token_stream is not None:
            self.token_stream_rewriter = TokenStreamRewriter(common_token_stream)
        else:
            raise TypeError("common_token_stream is None")

        self.method_name_list = []
        self.method_statements_list = {}  # dictionary that maps the methods to its statements
        self.method_body_list = {}  # dictionary that maps the methods to its body
        # getting targets
        self.target_package = target_package
        self.target_class = target_class
        self.target_method = target_method
        # tree helper variables
        self.is_in_target_package = False
        self.is_in_target_class = False
        self.is_in_a_method = False
        self.is_in_target_method = False
        self.current_method_name = ""
        self.used_variables = set([])
        self.lines = set([])
        self.variable_info = {'class': self.target_class, 'method': self.target_method, 'variables': {},
                              'formalParameters': {}}
        self.stack = []
        self.method_start_line = 0
        self.method_stop_line = 0
        self.start_line = staring_line
        self.length = length

    ######################################
    # Overriding required methods to satisfy our extraction requirements
    ######################################

    def enterPackageDeclaration(self, ctx: JavaParserLabeled.PackageDeclarationContext):
        if is_equivalent(ctx.getText()[:-1], self.target_package):
            self.is_in_target_package = True

    def exitPackageDeclaration(self, ctx: JavaParserLabeled.PackageDeclarationContext):
        if is_equivalent(ctx.getText()[:-1], self.target_package):
            self.is_in_target_package = False
            # todo: do code smell removal in phase 2

    def enterClassDeclaration(self, ctx: JavaParserLabeled.ClassDeclarationContext):
        if is_equivalent(ctx.IDENTIFIER(), self.target_class):
            self.is_in_target_class = True

    def exitClassDeclaration(self, ctx: JavaParserLabeled.ClassDeclarationContext):
        if is_equivalent(ctx.IDENTIFIER(), self.target_class):
            self.is_in_target_class = False
            # todo: do code smell removal in phase 2

    def enterMethodDeclaration(self, ctx: JavaParserLabeled.MethodDeclarationContext):
        self.is_in_a_method = True
        self.current_method_name = ctx.IDENTIFIER()
        # checking if current method is the target method
        if is_equivalent(self.current_method_name, self.target_method):
            self.is_in_target_method = True

        self.method_name_list.append(self.current_method_name)
        self.method_statements_list[self.current_method_name] = []
        self.method_start_line = ctx.start.line
        self.method_stop_line = ctx.stop.line

    def exitMethodDeclaration(self, ctx: JavaParserLabeled.MethodDeclarationContext):
        self.is_in_a_method = False
        if self.is_in_target_method:
            self.is_in_target_method = False
        # todo: do code smell removal in phase 2

    def enterMethodBody(self, ctx: JavaParserLabeled.MethodBodyContext):
        # todo: checking if the method is what we want then we extract it's body
        if self.is_in_target_class:
            if self.is_in_target_method:
                # number = ctx.getRuleIndex()
                # print(str(ctx.start)[-4:-3])
                # print(ParserRuleContext.setAltNumber(ctx, 10))
                # print(ctx.getToken())
                # print(number)
                # print(ctx.parser.getTokenStream().tokens)
                # print(ctx.parentCtx.getTokenStream().tokens)
                return
                # return
        # getting body of the method
        text = ctx.getText()
        # adding a new method body to method body list
        self.method_body_list[self.current_method_name] = text
        # removing '{' and '}' and ';' then splitting by ;
        text = text[1:-2].split(';')
        # creating an empty list of statements
        statement_list = []
        # adding each statement of the method with ';' at the end to statement list
        for each in text:
            statement_list.append(f'{each};')
        # adding a new method to method list with statements
        self.method_statements_list[self.current_method_name] = statement_list

    def enterLocalVariableDeclaration(self, ctx: JavaParserLabeled.LocalVariableDeclarationContext):
        if self.is_in_target_class and self.is_in_target_method:
            if ctx.start.line < self.start_line + self.method_start_line:
                self.variable_info['variables'][ctx.variableDeclarators().variableDeclarator()[
                    0].variableDeclaratorId().getText()] = ctx.typeType().getText()

    def enterFormalParameter(self, ctx: JavaParserLabeled.FormalParameterContext):
        if self.is_in_target_class and self.is_in_target_method:
            self.variable_info['formalParameters'][ctx.variableDeclaratorId().getText()] = ctx.typeType().getText()

    def enterEveryRule(self, ctx: ParserRuleContext):
        if self.is_in_target_class and self.is_in_target_method:
            if len(self.stack) == 0:
                start_line = ctx.start.line
                stop_line = ctx.stop.line
                # print(start_line ,'>=',self.start_line ,'+' ,self.method_start_line,'and', stop_line ,'<=',
                # self.start_line ,'+', self.method_start_line ,'+',self.length)
                if start_line >= self.start_line + self.method_start_line \
                        and stop_line < self.start_line + self.method_start_line + self.length:
                    # print('entered')
                    for i in range(start_line, stop_line + 1):
                        self.lines.add(i)
                    # print(ctx.getText())
                    self.stack.append(ctx)
                # else:
                #     if (start_line >= self.start_line + self.method_start_line) \
                #             != (stop_line < self.start_line + self.method_start_line + self.length):
                #         raise Exception('Input lines are not containing an entire command.')
            else:
                self.stack.append(ctx)

    def exitMethodBody(self, ctx: JavaParserLabeled.MethodBodyContext):
        pass

    def enterPrimary4(self, ctx: JavaParserLabeled.Primary4Context):
        if len(self.stack) != 0:
            if self.variable_info['variables'].keys().__contains__(str(ctx.IDENTIFIER())):
                self.used_variables.add(str(ctx.IDENTIFIER()))

    def exitEveryRule(self, ctx: ParserRuleContext):
        if len(self.stack) != 0:
            if self.stack[-1] == ctx:
                self.stack.pop()
            else:
                raise Exception


"""
    driver method
"""


def main(input_path, output_path, target_package, target_class, target_method):
    print("Started Extract Method")

    stream = FileStream(input_path, encoding='utf8')
    lexer = JavaLexer(stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParserLabeled(token_stream)
    parser.getTokenStream()
    parse_tree = parser.compilationUnit()
    my_listener = ExtractMethodRefactoring(common_token_stream=token_stream,
                                           target_package=target_package,
                                           target_class=target_class, target_method=target_method,
                                           staring_line=9, ending_line=11)

    walker = ParseTreeWalker()
    walker.walk(t=parse_tree, listener=my_listener)

    f = open(output_path, mode='w', newline='')
    text = str(datetime.datetime.now())
    f.write(f'// modified at: {text[:-7]}\n')
    text = my_listener.token_stream_rewriter.getDefaultText()
    f.write(text)
    f.flush()

    # for each in my_listener.method_name_list:
    # print(f'{each} : {my_listener.method_statements_list[each]}')
    # print(f'{each} : {my_listener.method_body_list[each]}')
    # print('*' * 10)

    print("Finished Extract Method")


if __name__ == '__main__':
    selectedFile = 'Test1.java'
    input_file = f"../tests/extract_method_tests/input_tests/{selectedFile}"
    # todo: remember in java we need the name of static classes to be exactly the same as file name
    output_file = f"../tests/extract_method_tests/output_tests/output-{selectedFile}"
    source_package = "Test1"
    source_class = "Test1"
    source_method = "a"
    main(input_file, output_file, source_package, source_class, source_method)
