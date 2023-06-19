import sys
from lex import *

# Parser object keeps track of current token and checks if code matches grammar
class Parser:
    def __init__(self, lexer, emitter):
        self.lexer = lexer
        self.emitter = emitter 
        
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
        self.emitter.header_line("#include <stdio.h>")
        self.emitter.header_line("int main(void){")

        # Skip leading newlines
        while self.check_token(TokenType.NEWLINE):  
            self.next_token()   
        
        # Parse all statements in program
        while not self.check_token(TokenType.EOF):
            self.statement()

        self.emitter.emit_line("return 0;")
        self.emitter.emit_line("}")

        for label in self.labels_gotoed:
            if label not in self.labels_declared:
                self.abort("Attempting to GOTO undeclared label: " + label)
        
        
    def statement(self):
        # PRINT (expression | string)
        if self.check_token(TokenType.PRINT):
            self.next_token()
             
            if self.check_token(TokenType.STRING):
                self.emitter.emit_line("printf(\"" + self.cur_token.text + "\\n\");")
                self.next_token()
            else:
                self.emitter.emit("printf(\"%" + ".2f\\n\", (float)(")
                self.expression()
                self.emitter.emit_line("));")

        # IF comparison THEN {statement} ENDIF
        elif self.check_token(TokenType.IF):
            self.next_token()
            self.emitter.emit("if(")
            self.comparison()
            self.match(TokenType.THEN)
            self.nl()
            self.emitter.emit_line("){")
            
            # Zero or more statements in the body
            while not self.check_token(TokenType.ENDIF):
                self.statement()    
            self.match(TokenType.ENDIF)
            self.emitter.emit_line("}")

        #WHILE comparison REPEAT {statement} ENDWHILE
        elif self.check_token(TokenType.WHILE):
            self.next_token()
            self.emitter.emit("while(")
            self.comparison()

            self.match(TokenType.REPEAT)
            self.nl()
            self.emitter.emit_line("){") 

            # Zero or more statments in the loop body
            while not self.check_token(TokenType.ENDWHILE):
                self.statement()

            self.match(TokenType.ENDWHILE)
            self.emitter.emit_line("}")

        # LABEL ident
        elif self.check_token(TokenType.LABEL):
            self.next_token()
            if self.cur_token.text in self.labels_declared: 
                self.abort("Label already exists: " + self.cur_token.text)
            self.labels_declared.add(self.cur_token.text)
            self.emitter.emit_line(self.cur_token.text + ":")
            self.match(TokenType.IDENT)

        # GOTO ident
        elif self.check_token(TokenType.GOTO):
            self.next_token()
            self.labels_gotoed.add(self.cur_token.text)
            self.emitter.emit_line("goto "  + self.cur_token.text + ";")
            self.match(TokenType.IDENT)

        # LET ident = expression
        elif self.check_token(TokenType.LET):
            self.next_token()

            #check if exists in symbol table
            if self.cur_token.text not in self.symbols:
                self.symbols.add(self.cur_token.text)
                self.emitter.header_line("float " + self.cur_token.text + ";")

            self.emitter.emit(self.cur_token.text + " = ")
            self.match(TokenType.IDENT)              
            self.match(TokenType.EQ)

            self.expression()
            self.emitter.emit_line(";")

        # INPUT ident
        elif self.check_token(TokenType.INPUT):
            self.next_token()
            if self.cur_token.text not in self.symbols:
                self.symbols.add(self.cur_token.text)
                self.emitter.header_line("float " + self.cur_token.text + ";")
            
            # Emit scanf and validate the input
            self.emitter.emit_line("if(0 == scanf(\"%" + "f\", &" + self.cur_token.text + ")) {")
            self.emitter.emit_line(self.cur_token.text + " = 0;")
            self.emitter.emit("scanf(\"%")
            self.emitter.emit_line("*s\");")
            self.emitter.emit_line("}")
            self.match(TokenType.IDENT)

        #Not valid 
        else:
            self.abort("Invalid statement at " + self.cur_token.text + " (" + self.cur_token.kind.name + ")")
                
        self.nl() #newline (as all statements are terminated with new lines)
    
   
    #comparison ::= expression ((== | != | > | >= | < | <=) expression)+
    def comparison(self):
        
        self.expression()
        # Must be at least one comparison operator and another expression
        if self.is_comparison_operator():
            self.emitter.emit(self.cur_token.text)
            self.next_token()
            self.expression()
        else:
            self.abort("Expected comparison operator at: " + self.cur_token.text)
    
        while self.is_comparison_operator():
            self.emitter.emit(self.cur_token.text)
            self.next_token()
            self.expression()

    def is_comparison_operator(self):
        return self.check_token(TokenType.GT) or self.check_token(TokenType.LT) or self.check_token(TokenType.GTEQ) or self.check_token(TokenType.LTEQ) or self.check_token(TokenType.EQEQ) or self.check_token(TokenType.NOTEQ)

    
    # expression ::= term {( - | + ) term}
    def expression(self):
        self.term()
        # Can have 0 or more +/- and expressions
        while self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.emitter.emit(self.cur_token.text)
            self.next_token()
            self.term()
    
    # term ::= unary {( / | * ) unary}
    def term(self):
        self.unary()
        # Can have 0 or more * / and expressions
        while self.check_token(TokenType.ASTERISK) or self.check_token(TokenType.SLASH):
            self.emitter.emit(self.cur_token.text)
            self.next_token()
            self.unary() 

    # unary ::= [ + | - ] primary
    def unary(self):
        if self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.emitter.emit(self.cur_token.text)
            self.next_token()
        self.primary()
    
    # primary ::= number | ident
    def primary(self):
        if self.check_token(TokenType.NUMBER):
            self.emitter.emit(self.cur_token.text)
            self.next_token()
        elif self.check_token(TokenType.IDENT):
            if self.cur_token.text not in self.symbols:
                self.abort("Referencing variable before assignment: " +self.cur_token.text)
            self.emitter.emit(self.cur_token.text)
            self.next_token()
        else:
            self.abort("Unexpected token at " + self.cur_token.text)

    def nl(self):
        # Require at least one new line
        self.match(TokenType.NEWLINE)
        #allows more than one new line at the end 
        while self.check_token(TokenType.NEWLINE):
            self.next_token()
               
