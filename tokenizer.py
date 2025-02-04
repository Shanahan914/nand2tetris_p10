class JackTokenizer:

    # class constants
    SYMBOLS = [
        '{', '}', '(', ')', '[', ']', '.', ',', ';', '+', 
        '-', '*', '/', '&', '|', '<', '>', '=', '~'
    ]
    KEYWORDS = [
        'class', 'constructor', 'function', 'method', 'field', 'static', 
        'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 
        'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'
    ]

    def __init__(self, input_file):
        self.current_file = input_file
        self.current_line = ''
        self.current_line_iter = iter(())
        self.current_token = ''
        self.current_char = 0
        self.is_string_val = False
        self.quote_type = None
        self.is_more_tokens = True
        self.current_char_global = None

        try:
            self.file = open(input_file, "r")
        except Exception as e:
            raise Exception(f"failed to read file ({input_file}) due to: {e}")

        # class constants
        

    def has_more_tokens(self):
        '''
            returns a boolean
        '''
        return self.is_more_tokens
 

    def advance(self):
        # NOTE : assuming that all input is valid and just outputting a string of tokens.
        '''
            returns the next token from the input and updates the current token.
            only called if has_more_tokens = True
            we go char by char, if current char is (' ', =, ., [, ())
        '''
        token = self._create_token()
        if token is not None:
            return
        self._get_next_line()
        token = self._create_token()
        if token is not None:
            return


    def _get_next_line(self):
        '''
            private method to select next non-empty line
        '''
        while True:
            try:
                ## handles advancing through the LINES of the file 

                # Read the next line and strip leading whitespace
                next_line = next(self.file).lstrip().rstrip()

                # Skip empty lines or comment-only lines
                if len(next_line) == 0 or next_line.startswith('/'):
                    continue
                
                # remove comments beginning with '//'
                next_line, _, _ = next_line.partition('//')
                next_line = next_line.rstrip()

                # Update internal state and return
                self.current_line = next_line
                self.current_line_iter = iter(self.current_line)
                return next_line
        
            except StopIteration:
                # Handle EOF
                self.is_more_tokens = False
                self.current_token = ''
                return None
    
    def _create_token(self):
        '''
            private method to create a valid token
        '''
        # empty string for token
        token_append = ''

        # 
        while True:
                # this func relies on a space to indicate end of a token. 
                # We therefore need to account for new tokens where a space is not needed. 
                # This always invovles symbols. Therefore, if we find a symbol we return the current token_append (if current_token > 0)
                # We then set current_char_global to the symbol and return in the next call to this func.
                if self.current_char_global:
                     self.current_token  = self.current_char_global
                     self.current_char_global = None
                     return self.current_token
                # get next char
                current_char = next(self.current_line_iter, None)

                # if at end of the current_line -> return none
                if current_char is None:
                    return None
                     
                # flag if we are in a string value
                # returns if it is the second instance of the same quotation type
                if current_char in {"'", '"'}:
                    if not self.is_string_val:
                        self.is_string_val = True
                        self.quote_type = current_char
                        continue
                    if current_char == self.quote_type:
                         # set instance vars back
                        self.is_string_val = False
                        self.quote_type = None
                        if len(token_append) > 0:
                            self.current_token = token_append
                            return self.current_token
                        continue

                # a symbol is always a standalone token
                if current_char in JackTokenizer.SYMBOLS:
                    if len(token_append)>0:
                        self.current_token = token_append
                        self.current_char_global = current_char
                        return self.current_token
                    else: 
                        self.current_token = current_char
                    return self.current_token
                
                # a space always indicates the end of a token
                if current_char == ' ':
                    self.current_char_global = None
                    if len(token_append) > 1:
                        self.current_token = token_append
                        return self.current_token
                    continue
                    
                
                # otherwise, append the char
                token_append += current_char
                


    def token_type(self):
        if len(self.current_token) == 0:
            return
        '''
            determines the type of the current token. 
            Returns string constant from following: 
            KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST

        '''
         # string val call
        if self.is_string_val:
            return 'STRING_CONST'
        
        # keyword call
        if self.current_token in JackTokenizer.KEYWORDS:
            return 'KEYWORD'

        # symbol call
        if self.current_token in JackTokenizer.SYMBOLS:
            return 'SYMBOL'
        
        # int_val
      
        try:  
            if self.current_token[0].isdigit():
                    return 'INT_CONST'
        except:
            return 'IDENTIFIER'
            
        
        return 'IDENTIFIER'

        
    def keyword(self):
        '''
            determines the type of keyword.
            Returns string constant from following: 
            CLASS, METHOD, FUNCTION, CONSTRUCTOR, INT, 
            BOOLEAN, CHAR, VOID, VAR, STATIC, 
            FIELD, LET, DO, IF, ELSE, WHILE, RETURN,
            TRUE, FALSE, NULL, THIS
        '''
        
        return self.current_token

    def symbol(self):
        '''
            determines the char in the symbol and 
            returns a char 
        '''
        return self.current_token

    def identifier(self):
        '''
            determines the identifer and 
            returns a string
        '''
        return self.current_token

    def int_val(self):
        '''
            determines the integer value of the current token and
            returns an int
        '''

        return self.current_token

    def string_val(self):
        '''
            determines the string value of the current token and
            returns a str
        '''
        return self.current_token