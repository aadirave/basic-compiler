import enum
import sys

class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENTIFIER = 2
    STRING = 3

    # reserved words
    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111

    # operators
    EQUALS = 201
    PLUS = 202
    MINUS = 203
    MULTIPLY = 204
    DIVIDE = 205
    CHECK_EQUALS = 206
    CHECK_NOT_EQUALS = 207
    LESS_THAN = 208
    LESS_THAN_EQUALS = 209
    GREATER_THAN = 210
    GREATER_THAN_EQUALS = 211

class Token:
    def __init__(self, token_txt, token_kind):
        self.text = token_txt
        self.kind = token_kind
    
    @staticmethod
    def check_keyword(tkn_text):
        for kind in TokenType:
            if kind.name == tkn_text and kind.value >= 100 and kind.value < 200:
                return kind
        
        return

class Lexer:
    def __init__(self, input):
        self.source = input + '\n'
        self.current_char = ''
        self.current_pos = -1 # increment to zero when starting to parse
        self.next_char()
    
    # get the next character
    def next_char(self):
        self.current_pos += 1

        if self.current_pos >= len(self.source):
            self.current_char = '\0' # end of file
        else:
            self.current_char = self.source[self.current_pos]

    # return the lookahead character
    def peek(self):
        if self.current_pos + 1 >= len(self.source):
            return '\0' # end of file
        else:
            return self.source[self.current_pos + 1]
    
    # invalid token, print error and exit
    def abort(self, err_message):
        sys.exit('Lexing error. ' + err_message)
    
    # skip whitespace except for newlines(code line delimiters)
    def skip_whitespace(self):
        while self.current_char == ' ' or self.current_char == '\t' or self.current_char == '\r':
            self.next_char()

    def ignore_comments(self):
        if self.current_char == '#':
            while self.current_char != '\n':
                self.next_char()
    
    # get the next token
    def get_token(self):
        self.skip_whitespace() # ignore spaces
        self.ignore_comments() # ignore comments

        if self.current_char == '+':
            tkn = Token(self.current_char, TokenType.PLUS)
        elif self.current_char == '-':
            tkn = Token(self.current_char, TokenType.MINUS)
        elif self.current_char == '*':
            tkn = Token(self.current_char, TokenType.MULTIPLY)
        elif self.current_char == '/':
            tkn = Token(self.current_char, TokenType.DIVIDE)
        elif self.current_char == '\n':
            tkn = Token(self.current_char, TokenType.NEWLINE)
        elif self.current_char == '\0':
            tkn = Token(self.current_char, TokenType.EOF)
        elif self.current_char == '=':
            # check if it's assignment or check for equality
            if self.peek() == '=':
                last_char = self.current_char
                self.next_char()
                tkn = Token(last_char + self.current_char, TokenType.CHECK_EQUALS)
            else:
                tkn = Token(self.current_char, TokenType.EQUALS)
        elif self.current_char == '>':
            # check if it's > or >=
            if self.peek() == '=':
                last_char = self.current_char
                self.next_char()
                tkn = Token(last_char + self.current_char, TokenType.GREATER_THAN_EQUALS)
            else:
                tkn = Token(self.current_char, TokenType.GREATER_THAN)
        elif self.current_char == '<':
            # check if it's < or <=
            if self.peek() == '=':
                last_char = self.current_char
                self.next_char()
                tkn = Token(last_char + self.current_char, TokenType.LESS_THAN_EQUALS)
            else:
                tkn = Token(self.current_char, TokenType.LESS_THAN)
        elif self.current_char == '!':
            if self.peek() == '=':
                last_char = self.current_char
                self.next_char()
                tkn = Token(last_char + self.current_char, TokenType.CHECK_NOT_EQUALS)
        elif self.current_char == '\"':
            # get the string between quotations
            self.next_char()
            start_pos = self.current_pos

            while self.current_char != '\"':
                # making it easier to deal with C later on
                if self.current_char == '\r' or self.current_char == '\n' or self.current_char == '\t' or self.current_char == '\\' or self.current_char == '%':
                    self.abort('Illegal character in the string')

                self.next_char()
            
            tkn_text = self.source[start_pos:self.current_pos]
            tkn = Token(tkn_text, TokenType.STRING)
        elif self.current_char.isdigit():
            # get all digits and decimals if present
            start_pos = self.current_pos

            while self.peek().isdigit():
                self.next_char()
            if self.peek() == '.':
                # dealing with the decimal point
                self.next_char()

                if not self.peek().isdigit():
                    self.abort('Illegal character in number')
                while self.peek().isdigit():
                    self.next_char()
            
            tkn_text = self.source[start_pos:self.current_pos + 1]
            tkn = Token(tkn_text, TokenType.NUMBER)
        elif self.current_char.isalpha():
            # must be an identifier or keyword
            start_pos = self.current_pos
            while self.peek().isalnum():
                self.next_char()

            tkn_text = self.source[start_pos:self.current_pos + 1]
            keyword = Token.check_keyword(tkn_text)

            if keyword == None:
                tkn = Token(tkn_text, TokenType.IDENTIFIER)
            else:
                tkn = Token(tkn_text, keyword)
        else:
            self.abort('Unknown token: ' + self.current_char)

        self.next_char()
        return tkn
        
