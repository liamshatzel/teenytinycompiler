import enum
import sys
class Lexer:
    
    def  __init__(self, source):
        self.source = source + '\n' # Source code to lex as a string (append newline to know where end is)
        self.cur_char = '' # Current character in the string.
        self.cur_pos = -1 #current position in the string
        self.next_char()
    
    # Process next character
    def next_char(self):
        self.cur_pos += 1
        if self.cur_pos >= len(self.source):
            self.cur_char = '\0' #EOF 
        else:
            self.cur_char = self.source[self.cur_pos]
    
   # Return the lookahead character (get upcoming char without incrementing curpos)
    def peek(self):
       if self.cur_pos + 1 >= len(self.source):
            return '\0'
       return self.source[self.cur_pos + 1]
    
    # Invalid token found, print error message and exit
    def abort(self, message):
        sys.exit("Lexing error. " + message)
    
    # Skip whitespace except newlines (used to indicate end of statement)
    def skip_whitespace(self):
        while self.cur_char == ' ' or self.cur_char == '\t' or self.cur_char == '\r':
            self.next_char()
    
    # Skip comments in the code 
    def skip_comment(self):
        if self.cur_char == '#':
            while self.cur_char != '\n':
                self.next_char()
        
    # Return the next token (also classifies token)
    def get_token(self):
        # Check the first character of the token to see if we can tell what it is
        # If it is a multiple character operator then it will be processed after
        self.skip_whitespace()
        self.skip_comment()
        token = None
        
        if self.cur_char == '+':
            token = Token(self.cur_char , TokenType.PLUS)
        elif self.cur_char == '-':
            token = Token(self.cur_char , TokenType.MINUS)
        elif self.cur_char == '*':
            token = Token(self.cur_char , TokenType.ASTERISK)
        elif self.cur_char == '/':
            token = Token(self.cur_char , TokenType.SLASH)
        elif self.cur_char == '\n':
            token = Token(self.cur_char , TokenType.NEWLINE)
        elif self.cur_char ==  '\0':
            token = Token('', TokenType.EOF)
        elif self.cur_char == '=':
            if self.peek() == '=':
                prev_char = self.cur_char
                self.next_char()
                token = Token(prev_char + self.cur_char, TokenType.EQEQ)
            else:
                token = Token(self.cur_char, TokenType.EQ)
        elif self.cur_char == '>':
            if self.peek() == '=':
                prev_char = self.cur_char
                self.next_char()
                token = Token(prev_char + self.cur_char, TokenType.GTEQ)
            else:
                token = Token(self.cur_char, TokenType.GT)
        elif self.cur_char == '<':
            if self.peek() == '=':
                prev_char = self.cur_char
                self.next_char()
                token = Token(prev_char + self.cur_char, TokenType.LTEQ)
            else:
                token = Token(self.cur_char, TokenType.LT)
        elif self.cur_char == '!':
            if self.peek() == '=':
                prev_char = self.cur_char
                self.next_char()
                token = Token(prev_char + self.cur_char, TokenType.NOTEQ)
            else:
                self.abort("Expected !=, got !" + self.peek())
        elif self.cur_char == '\"': #tokenize strings
            self.next_char()
            start_pos = self.cur_pos
            while self.cur_char != '\"':
                if self.cur_char == '\r' or self.cur_char == '\n' or self.cur_char == '\t' or self.cur_char == '\\' or self.cur_char == '%':
                    self.abort("Illegal character in string")
                self.next_char()
            tok_text = self.source[start_pos : self.cur_pos] #token of substring which makes up cur string
            token = Token(tok_text, TokenType.STRING)
        elif self.cur_char.isdigit():
            #leading char is digit => must be number
            start_pos = self.cur_pos
            while self.peek().isdigit():
                self.next_char()
            if self.peek() == '.':
                self.next_char()
                if not self.peek().isdigit():
                    self.abort("Illegal character in number.")
                while self.peek().isdigit():
                    self.next_char()
            tok_text = self.source[start_pos : self.cur_pos + 1] #goes to +1 bc of peek
            token = Token(tok_text, TokenType.NUMBER)
        elif self.cur_char.isalpha(): #tokenize keywords
            #leading character is letter
            #get all consecutive letters/digits
            start_pos = self.cur_pos
            while self.peek().isalnum():
                self.next_char()
            tok_text = self.source[start_pos : self.cur_pos + 1]
            # check if its a keyword
            keyword = Token.check_if_keyword(tok_text)
            if keyword == None:
                token = Token(tok_text, TokenType.IDENT)
            else:
                token = Token(tok_text, keyword)

        else:
            self.abort("Unknown token: " + self.cur_char)
        self.next_char()
        return token

class Token:
    def __init__(self, token_text, token_kind):
        self.text = token_text #actual string of token
        self.kind = token_kind #what type of token it is

    @staticmethod
    def check_if_keyword(token_text):
        for kind in TokenType:
            #check if token exists in enum
            if kind.name == token_text and kind.value >= 100 and kind.value  < 200:
                return kind
        return None


class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3
    #KEYWORDS
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
    #OPERATORS
    EQ = 201
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211
    
