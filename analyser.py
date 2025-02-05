from tokenizer import JackTokenizer
from compilation_engine import CompilationEngine
import sys
import os

###
## process args and set outfile 
###

# must provide a file or folder
if len(sys.argv) < 2:
    raise Exception('You must provide a .asm file or a folder to translate')

# get cli file or folder arg
file_obj = sys.argv[1]

# check that file or folder exists
if not os.path.exists(file_obj):
    raise Exception(f'You have not provided a valid file or folder" {file_obj}.')

# collect .vm files
jack_files = []

# check if arg is a .vm file and add
if file_obj.endswith('.jack'):
    jack_files.append(file_obj)
# otherwise if folder, loop round the files and add the .vm files
else:
    for file in os.listdir(str(file_obj)):
        if file.endswith('.jack'):
            file_with_path = file_obj + '/' + file
            jack_files.append(file_with_path)

# if no files in asm_files, raise exception
if len(jack_files) < 1:
    raise Exception('Failed to find any .vm files in the provided file or folder')

# outfile name 
if os.path.isdir(file_obj):
    dir_name = os.path.basename(file_obj)
    out_file = os.path.join(file_obj, f"{dir_name}.xml")
else:
    file_name, _ = os.path.splitext(file_obj)
    out_file = f"{file_name}.xml"


###
## initialise and run program
###

# initialize the codewriter 

# loop through each vm file
for file in jack_files:

    # initialize a parser
    tokenizer = JackTokenizer(file)

    # get name of current file
    file_name, rest= os.path.splitext(file)

    split_name = os.path.basename(file)
    name_without_extension = os.path.splitext(split_name)[0]

   # create name for out file
    out_file = name_without_extension + ".xml"

    # initialize a compilation engine
    compilation_engine = CompilationEngine(tokenizer, out_file )

    tokenizer.advance()
    # loop through each line in the current file
    while tokenizer.has_more_tokens():
        token_type = tokenizer.token_type()

        # keyword call
        if token_type == 'KEYWORD':
            current_token = tokenizer.keyword()
            if current_token == 'while':
                compilation_engine.compile_while()
            elif current_token == 'do':
                compilation_engine.compile_do()
            elif current_token == 'let':
                compilation_engine.compile_let()
            elif current_token == 'return':
                compilation_engine.compile_return()
            elif current_token == 'class':
                compilation_engine.compile_class()
            elif current_token in ('method', 'function', 'constructor'):
                compilation_engine.compile_subroutine()
            elif current_token in ('static', 'field'):
                compilation_engine.compile_subroutine()
            elif current_token in ('static', 'field'):
                compilation_engine.compile_subroutine()

        # symbol call
        if token_type == 'SYMBOL':
            current_token = tokenizer.symbol()

         # symbol call
        if token_type == 'IDENTIFIER':
            current_token = tokenizer.identifier()
        
        # int_val
        if token_type == 'INT_CONST':
            current_token = tokenizer.int_val()
        
        # otherwise, must be identifer
        if token_type == 'STRING_CONST':
            current_token = tokenizer.string_val()
        

print('finished')
