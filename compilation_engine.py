class CompilationEngine:

    def __init__(self, tokenizer, out_file):
        self.tokenizer = tokenizer
        self.out_file = out_file
        self.indent_level = 0

        try:
            self.file = open(out_file, 'a')
        except Exception as e:
            raise Exception("failed to read file ({file}) due to: {e}")
        
        # mapping keywords to the correct methods in tokenizer
        self.keyword_to_func ={
            'STRING_CONST': self.tokenizer.string_val,
            'KEYWORD' : self.tokenizer.keyword,
            'SYMBOL' : self.tokenizer.symbol,
            'INT_CONST' : self.tokenizer.int_val,
            'IDENTIFIER' : self.tokenizer.identifier
            }


    def compile_class(self):
        pass

    def complie_class_var_dec(self):
        pass

    def compile_subroutine(self):
        pass

    def compile_parameter_list(self):
        pass

    def compile_var_dec(self):
        pass

    def compile_statements(self):
        pass

    def compile_do(self):
        # opening tag
        self._write_tag('doStatement')

        # increase indent 
        self.indent_level += 1
        self._write_tag('keyword', 'do')
        

    def compile_let(self):
        pass

    def compile_while(self):
        # opening tag
        self._write_tag('whileStatement')

        # increase indent 
        self.indent_level += 1
        self._write_tag('keyword', 'while')
        
        # rule 1 - must be '('
        if self._advance_and_check('SYMBOL', '('):
            self._write_tag('symbol', '(')
            
        # rule 2 - call expression
        self.compile_expression()

        # rule 3 - must be ')'
        if self._advance_and_check('SYMBOL', ')'):
            self._write_tag('symbol', ')')

        # rule 4 - must be '{'
        if self._advance_and_check('SYMBOL', '{'):
            self._write_tag('symbol', '{')

        # rule 5 - call statements
        self.compile_statements()

        # rule 6 - must be '}'
        if self._advance_and_check('SYMBOL', '}'):
            self._write_tag('symbol', '}')

        # decrement indent
        self.indent_level -= 1

        # close
        self._write_tag('/whileStatement')

        # advance and return
        self.tokenizer.advance()
        return 
  

    def compile_return(self):
        # open  tag
        self._write_tag('returnStatement')

        # increase indent 
        self.indent_level += 1
        self._write_tag('keyword','return')

        # check for expression
        if not self._check_for_option('SYMBOL', ';'):
            self.compile_expression()
            if not self._advance_and_check('SYMBOL', ';'):
                raise Exception("Expected to see ';'")
        
        self._write_tag('symbol', ';')

        # decrement indent
        self.indent_level -= 1
        
        # close tag
        self._write_tag('/returnStatement')

        # advance and return
        self.tokenizer.advance()
        return 


    def compile_if(self):
         # opening tag
        self._write_tag('ifStatement')

        ## MANDTORY IF CLAUSE

        # increase indent 
        self.indent_level += 1
        self._write_tag('keyword', 'if')
        
        # rule - must be '('
        if self._advance_and_check('SYMBOL', '('):
            self._write_tag('symbol', '(')
            
        # rule - call expression
        self.compile_expression()

        # rule - must be ')'
        if self._advance_and_check('SYMBOL', ')'):
            self._write_tag('symbol', ')')

        # rule - must be '{'
        if self._advance_and_check('SYMBOL', '{'):
            self._write_tag('symbol', '{')

        # rule - call statements
        self.compile_statements()

        # rule - must be '}'
        if self._advance_and_check('SYMBOL', '}'):
            self._write_tag('symbol', '}')


        ## OPTIONAL ELSE CLAUSE

        # advance and check if we have an else statement
        if self._check_for_option('KEYWORD', 'else'):
            self._write_tag('keyword', 'else')

            # rule - must be '{'
            if self._advance_and_check('SYMBOL', '{'):
                self._write_tag('symbol', '{')

            # rule - call statements
            self.compile_statements()

            # rule - must be '}'
            if self._advance_and_check('SYMBOL', '}'):
                self._write_tag('symbol', '}')
            
            # advance again
            self.tokenizer.advance()
        
        # decrement indent
        self.indent_level -= 1

        # close
        self._write_tag('/ifStatement')


    
    def compile_expression(self):
        pass

    def compile_term(self):
        pass

    def compile_expression_list(self):
        pass

        #
    ### HELPER FUNCTIONS 
        #  
    def _write_tag(self, tag, content=None):
        indent = "  " * self.indent_level
        if content:
            self.file.write( f"{indent}<{tag}> {content} </{tag}>\n")
        else:
            self.file.write( f"{indent}<{tag}>\n")
    
    def _advance_and_check(self, keyword, content):
        # get next token
        self.tokenizer.advance()

        # get token type    
        token_type = self.tokenizer.token_type()

        # get current token
        if keyword in self.keyword_to_func:
            current_token = self.keyword_to_func[keyword]()
        else:
            raise Exception(f"Failed to select getter method for token")
        
        # check and return
        if token_type == keyword and current_token == content :
            return True
        else:
            raise Exception(f"Grammar error. Expected '{content}' but receieved {current_token}")

    def _check_for_option(self, keyword, content):
         # get next token
        self.tokenizer.advance()

        # get token type    
        token_type = self.tokenizer.token_type()

        # get current token
        if keyword in self.keyword_to_func:
            current_token = self.keyword_to_func[keyword]()
        else:
            raise Exception(f"Failed to select getter method for token")
        
        # check and return
        if token_type == keyword and current_token == content :
            return True
        else:
            return False
        
    def _close_tag(self, content):
        # decrement indent
        self.indent_level -= 1

        # close
        self._write_tag(f'/{content}')

        # advance and return
        self.tokenizer.advance()