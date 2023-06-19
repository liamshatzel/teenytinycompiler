import sys
from lex import *

# Parser object keeps track of current token and checks if code matches grammar
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        
        self.symbols = set()
        self.labels_declared = set()     
        self.labels_gotoed = set()       
 
        self.cur_token = None
        self.peek_token = None
        self.next_token()
        self.next_token() # two calls to get current and peek
    
    # Returns true if current token matches
    def check_token(self, kind):
        return kind == self.cur_token.kind
    
    #Return true if next token matches
    def check_peek(self, kind):
        return kind == self.peek_token.kind
    
    # Try to match current token. If not, error. Advances current token
    def match(self, kind):
        if not self.check_token(kind):
            self.abort("Expected " + kind.name + ", got " + self.cur_token.kind.name)
        self.next_token()

    # advances the current token 
    def next_token(self):
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.get_token() 
         
    def abort(self, message):
        sys.exit("Error. " + message)
    
    # Production rules:
    
    #program ::= {statement}
    #{} zero or more [] zero or one + one or more
    def program(self):
        print("PROGRAM")

        # Skip leading newlines
        while self.check_token(TokenType.NEWLINE):  
            self.next_token()   
        while not self.check_token(TokenType.EOF):
            self.statement()
        for label in self.labels_gotoed:
            if label not in self.labels_declared:
                self.abort("Attempting to GOTO undeclared label: " + label)
        
    def statement(self):
        if self.check_token(TokenType.PRINT):
            print("STATEMENT-PRINT")
            self.next_token()
        
            if self.check_token(TokenType.STRING):
                self.next_token()
            else:
                self.expression()

        # IF comparison THEN {statement} ENDIF
        elif self.check_token(TokenType.IF):
            print("STATEMENT-IF")
            self.next_token()
            self.comparison()
            self.match(TokenType.THEN)
            self.nl()
            
            # Zero or more statements in the body
            while not self.check_token(TokenType.ENDIF):
                self.statement()    
            self.match(TokenType.ENDIF)

        #WHILE comparison REPEAT {statement} ENDWHILE
        elif self.check_token(TokenType.WHILE):
            print("STATEMENT-WHILE")
            self.next_token()
            self.comparison()

            self.match(TokenType.REPEAT)
            self.nl()
            
            # Zero or more statments in the loop body
            while not self.check_token(TokenType.ENDWHILE):
                self.statement()

            self.match(TokenType.ENDWHILE)

        # LABEL ident
        elif self.check_token(TokenType.LABEL):
            print("STATEMENT-LABEL")
            self.next_token()
            if self.cur_token.text in self.labels_declared: 
                self.abort("Label already exists: " + self.cur_token.text)
            self.labels_declared.add(self.cur_token.text)
            self.match(TokenType.IDENT)

        # GOTO ident
        elif self.check_token(TokenType.GOTO):
            print("STATEMENT-GOTO")
            self.next_token()
            self.labels_gotoed.add(self.cur_token.text)
            self.match(TokenType.IDENT)

        # LET ident = expression
        elif self.check_token(TokenType.LET):
            print("STATEMENT-LET")
            self.next_token()

            #check if exists in symbol table
            if self.cur_token.text not in self.symbols:
                self.symbols.add(self.cur_token.text)
    
            self.match(TokenType.IDENT)              
            self.match(TokenType.EQ)

            self.expression()

        # INPUT ident
        elif self.check_token(TokenType.INPUT):
            print("STATEMENT-INPUT")
            self.next_token()
            if self.cur_token.text not in self.symbols:
                self.symbols.add(self.cur_token.text)
            self.match(TokenType.IDENT)

        #Not valid 
        else:
            self.abort("Invalid statement at " + self.cur_token.text + " (" + self.cur_token.kind.name + ")")
                
        self.nl() #newline (as all statements are terminated with new lines)
    
   
    #comparison ::= expression ((== | != | > | >= | < | <=) expression)+
    def comparison(self):
        print("COMPARISON")
        
        self.expression()
        # Must be at least one comparison operator and another expression
        if self.is_comparison_operator():
            self.next_token()
            self.expression()
        else:
            self.abort("Expected comparison operator at: " + self.cur_token.text)
    
        while self.is_comparison_operator():
            self.next_token()
            self.expression()

    def is_comparison_operator(self):
        return self.check_token(TokenType.GT) or self.check_token(TokenType.LT) or self.check_token(TokenType.GTEQ) or self.check_token(TokenType.LTEQ) or self.check_token(TokenType.EQEQ) or self.check_token(TokenType.NOTEQ)

    
    # expression ::= term {( - | + ) term}
    def expression(self):
        print("EXPRESSION")
        self.term()

        # Can have 0 or more +/- and expressions
        while self.check_token(TokenType.PLUS or self.check_token(TokenType.MINUS)):
            self.next_token()
            self.term()
    
    # term ::= unary {( / | * ) unary}
    def term(self):
        print("TERM")
        
        self.unary()
        # Can have 0 or more * / and expressions
        while self.check_token(TokenType.ASTERISK) or self.check_token(TokenType.SLASH):
            self.next_token()
            self.unary() 

    # unary ::= [ + | - ] primary
    def unary(self):
        print("UNARY")
        
        if self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.next_token()
        self.primary()
    
    # primary ::= number | ident
    def primary(self):
        print("PRIMARY (" + self.cur_token.text + ")")
    
        if self.check_token(TokenType.NUMBER):
            self.next_token()
        elif self.check_token(TokenType.IDENT):
            if self.cur_token.text not in self.symbols:
                self.abort("Referencing variable before assignment: " +self.cur_token.text)
            self.next_token()
        else:
            self.abort("Unexpected token at " + self.cur_token.text)

    def nl(self):
        print("NEWLINE")

        # Require at least one new line
        self.match(TokenType.NEWLINE)
        #allows more than one new line at the end 
        while self.check_token(TokenType.NEWLINE):
            self.next_token()
               
