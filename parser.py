import sys
from lexer import *

# checks if input is compatible with the syntax
class Parser:
    def __init__(self, lexer, generator):
        self.lexer = lexer
        self.generator = generator
        
        # keeps track of variables and labels declared and gotoed
        self.symbols = set()
        self.labels_declared = set()
        self.labels_gotoed = set()

        self.current_token = None
        self.peek_token = None

        # calling twice to initialize both variables
        self.next_token()
        self.next_token()

    # checks if the current token matches
    def check_token(self, kind):
        return kind == self.current_token.kind

    # checks if the next token matches
    def check_peek(self, kind):
        return kind == self.peek_token.kind

    # try to match the current token and then advance
    def match(self, kind):
        if not self.check_token(kind):
            self.abort('Expected ' + kind.name + ', but got ' + self.current_token.kind.name)
        
        self.next_token()

    # advances the current token
    def next_token(self):
        self.current_token = self.peek_token
        self.peek_token = self.lexer.get_token()

    def abort(self, err_message):
        sys.exit('Error. ' + err_message)
            
    def newline(self):
        # print('NEWLINE')

        self.match(TokenType.NEWLINE)
        while self.check_token(TokenType.NEWLINE):
            self.next_token()
    
    def is_comparison_operator(self):
        return self.check_token(TokenType.GREATER_THAN) or self.check_token(TokenType.GREATER_THAN_EQUALS) or self.check_token(TokenType.CHECK_EQUALS) or self.check_token(TokenType.CHECK_NOT_EQUALS) or self.check_token(TokenType.LESS_THAN_EQUALS) or self.check_token(TokenType.LESS_THAN)

    # defining rules

    # program ::= {statements}
    def program(self):
        self.generator.header_line('#include <iostream>')
        self.generator.header_line('#include <cstdio>')
        self.generator.header_line('using namespace std;')
        self.generator.header_line('int main() {')

        # skip newlines at the start
        while self.check_token(TokenType.NEWLINE):
            self.next_token()

        # parsing all the statements in the program
        while not self.check_token(TokenType.EOF):
            self.statement()
        
        self.generator.generate_line('return 0;')
        self.generator.generate_line('}')

        # check that all labels used in gotos are declared
        for label in self.labels_gotoed:
            if label not in self.labels_declared:
                self.abort('Attempting to goto to undefined label: ' + label)

    
    def statement(self):
        # checking what type of statement it is

        # PRINT (expression | string)
        if self.check_token(TokenType.PRINT):
            # print('STATEMENT-PRINT')
            self.next_token()

            if self.check_token(TokenType.STRING):
                # simple string to print
                self.generator.generate_line('cout << \"' + self.current_token.text + '\\n\";')
                self.next_token()
            else:
                self.generator.generate('cout << ')
                self.expression()
                self.generator.generate_line(' << endl;')

        # IF comparison THEN \n statement \n ENDIF
        elif self.check_token(TokenType.IF):
            # print('STATEMENT-IF')
            self.next_token()
            self.generator.generate('if(')
            self.comparison()
            
            self.match(TokenType.THEN)
            self.newline()
            self.generator.generate_line(') {')

            while not self.check_token(TokenType.ENDIF):
                self.statement()
            
            self.match(TokenType.ENDIF)
            self.generator.generate_line('}')
        
        # WHILE comparison REPEAT \n statement \n ENDWHILE
        elif self.check_token(TokenType.WHILE):
            # print('STATEMENT-WHILE')
            self.next_token()
            self.generator.generate('while(')
            self.comparison()

            self.match(TokenType.REPEAT)
            self.newline()
            self.generator.generate_line(') {')

            while not self.check_token(TokenType.ENDWHILE):
                self.statement()
            
            self.match(TokenType.ENDWHILE)
            self.generator.generate_line('}')
        
        # LABEL identifier
        elif self.check_token(TokenType.LABEL):
            # print('STATEMENT-LABEL')
            self.next_token()

            # check if the label already exists
            if self.current_token.text in self.labels_declared:
                self.abort('Label already defined: ' + self.current_token.text)
            self.labels_declared.add(self.current_token.text)

            self.generator.generate_line(self.current_token.text + ':')
            self.match(TokenType.IDENTIFIER)
        
        # GOTO identifier
        elif self.check_token(TokenType.GOTO):
            # print('STATEMENT-GOTO')
            self.next_token()
            self.labels_gotoed.add(self.current_token.text)
            self.generator.generate_line('goto ' + self.current_token.text + ';')
            self.match(TokenType.IDENTIFIER)
        
        # LET identifier = expression
        elif self.check_token(TokenType.LET):
            # print('STATEMENT-LET')
            self.next_token()

            # declaring the variable
            if self.current_token.text not in self.symbols:
                self.symbols.add(self.current_token.text)
                self.generator.header_line('float ' + self.current_token.text + ';') # sending it to the top for easier debugging

            self.generator.generate(self.current_token.text + ' = ')
            self.match(TokenType.IDENTIFIER)
            self.match(TokenType.EQUALS)

            self.expression()
            self.generator.generate_line(';')
        
        # INPUT identifier
        elif self.check_token(TokenType.INPUT):
            # print('STATEMENT-INPUT')
            self.next_token()

            # declaring the variable if not already done
            if self.current_token.text not in self.symbols:
                self.symbols.add(self.current_token.text)
                self.generator.header_line('float ' + self.current_token.text + ';')

            self.generator.generate('cin >> ' + self.current_token.text + ';\n')
            self.match(TokenType.IDENTIFIER)
        
        # invalid statement
        else:
            self.abort('Invalid statement at ' + self.current_token.text + ' (' + self.current_token.kind.name + ')')


        self.newline()
    
    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)
    def comparison(self):
        # print('COMPARISON')

        self.expression()
        # at least one comparison operator and another expression needed
        if self.is_comparison_operator():
            self.generator.generate(self.current_token.text)
            self.next_token()
            self.expression()

        while self.is_comparison_operator():
            self.generator.generate(self.current_token.text)
            self.next_token()
            self.expression()
    
    # expression ::= term {(- | +) term}
    def expression(self):
        # print('EXPRESSION')

        self.term()
        while self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.generator.generate(self.current_token.text)
            self.next_token()
            self.term()
    
    # term ::= unary {(/ | *) unary}
    def term(self):
        # print('TERM')
        
        self.unary()
        while self.check_token(TokenType.MULTIPLY) or self.check_token(TokenType.DIVIDE):
            self.generator.generate(self.current_token.text)
            self.next_token()
            self.unary()

    # unary ::= [+ | -] primary
    def unary(self):
        # print('UNARY')

        if self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.generator.generate(self.current_token.text)
            self.next_token()
        
        self.primary()
    
    # primary ::= number | identifier
    def primary(self):
        # print('PRIMARY (' + self.current_token.text + ')')

        if self.check_token(TokenType.NUMBER):
            self.generator.generate(self.current_token.text)
            self.next_token()
        elif self.check_token(TokenType.IDENTIFIER):
            # check that the variable actually exists
            if self.current_token.text not in self.symbols:
                self.abort('Referencing variable before assignment: ' + self.current_token.text)

            self.generator.generate(self.current_token.text)
            self.next_token()
        else:
            self.abort('Unexpected token at ' + self.current_token.text)
