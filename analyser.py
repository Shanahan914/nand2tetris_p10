from tokenizer import JackTokenizer
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

    # set file name in codewriter
    

    # loop through each line in the current file
    while tokenizer.has_more_tokens():
        tokenizer.advance()
        print(tokenizer.token_type())

print('finished')
