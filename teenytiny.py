from lex import *
from parse import *
from emit import *
import sys

def main():
    print("Teeny Tiny Compiler!")
    
    if len(sys.argv) != 2:
            sys.exit("Error: Compiler needs source file as argument.")
    with open(sys.argv[1], 'r') as input_file:
            source = input_file.read()
    
    #lexer, emitter, parser         
    lexer = Lexer(source)
    emitter = Emitter("out.c")
    parser = Parser(lexer, emitter) 
    
    parser.program() #start parser
    emitter.write_file()    
    print("Compiling Complete")
    
main()
