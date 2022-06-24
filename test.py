from lexer import *
from parser import *
from generator import *
import sys

if len(sys.argv) != 2:
    sys.exit('Error: compiler needs file to parse.')

with open(sys.argv[1], 'r') as input_file:
    input = input_file.read()

lex = Lexer(input)
generator = Generator('out.cpp')
parser = Parser(lex, generator)

parser.program()
generator.write_file()
print('Compiling completed.')
