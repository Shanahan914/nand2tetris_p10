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
        # opening tag
        self._write_tag('class')

        # check first token
        if self._first_token_tag('KEYWORD', 'class'):
            self._write_tag('keyword', 'class')
        
        # rule - must be identifier
        if self._advance_and_check_type_only('IDENTIFIER'):
            current_token = self.tokenizer.identifier()
            self._write_tag('identifier', current_token)
        
        # rule - must be '{'
        if self._advance_and_check('SYMBOL', '{'):
            self._write_tag('symbol', '{')
        
        # rule - call classVarDec
        self.tokenizer.advance()
        while self._check_classVarDec():
            self.complie_class_var_dec()

         # rule - call subroutine
        while self._check_subroutineDec():
            self.compile_subroutine()
            
        # rule - must be '}'
        if self._only_check('SYMBOL', '}'):
            self._write_tag('symbol', '}')

        # close
        self._close_tag('/class')

        return 
  

    def complie_class_var_dec(self):
         # opening tag
        self._write_tag('classVarDec')

        # check first token
        if self._check_classVarDec():
            self.indent_level += 1
            self._write_tag('keyword', self.tokenizer.keyword())
        
        # rule - must be a type
        self.tokenizer.advance()
        if self._check_is_type():
            self._write_tag(self.tokenizer.token_type(), self.tokenizer.keyword())
        
        # rule - must be varName
        if self._advance_and_check_type_only('IDENTIFIER'):
            self._write_tag('identifier', self.tokenizer.identifier())
        
        # rule - optional list of (, varName)
        while self._advance_and_check_for_option('SYMBOL', ','):
            self._write_tag('symbol', ',')
            if self._advance_and_check_type_only('identifier'):
                self._write_tag('identifier', self.tokenizer.identifier())
            
        # rule - must be ';'
        if self._only_check('SYMBOL', ';'):
            self._write_tag('symbol', ';')

        # close tag
        self._close_tag('/classVarDec')

        return


    def compile_subroutine(self):
         # opening tag
        self._write_tag('subroutineDec')

        # check first token
        if self._check_subroutineDec():
            self.indent_level += 1
            self._write_tag('keyword', self.tokenizer.keyword())
        
        # rule - must be a type or void
        self.tokenizer.advance()
        if self._check_is_type() or self.tokenizer.keyword() == 'void':
            self._write_tag(self.tokenizer.token_type(), self.tokenizer.keyword())
        
        # rule - must be identifier
        if self._advance_and_check_type_only('IDENTIFIER'):
            self._write_tag('identifier', self.tokenizer.identifier())

         # rule - must be '('
        if self._advance_and_check('SYMBOL', '('):
            self._write_tag('symbol', '(')
            
        # rule - call parameterList
        self.tokenizer.advance()
        self.compile_parameter_list()

        # rule - must be ')'
        if self._only_check('SYMBOL', ')'):
            self._write_tag('symbol', ')')

        # rule - must be subroutineBody
        self.tokenizer.advance()
        self._compile_subroutine_body()

        # close tag
        self.indent_level -= 1
        self._write_tag('/subroutineDec')

        return
    
    def _compile_subroutine_body(self):
             # opening tag
        self._write_tag('subroutineBody')

        # check first token - must be '{'
        if self._first_token_tag('SYMBOL', '{'):
            self._write_tag('symbol', '{')

        # rule - optional varDec
        self.tokenizer.advance()
        while self.tokenizer.token_type() == 'KEYWORD' and self.tokenizer.keyword() == 'var':
            self.compile_var_dec()
        
        # rule - call statements
        self.compile_statements()

        # rule - must be '}'
        if self._only_check('SYMBOL','}'):
            self._write_tag('symbol', '}')

        # close tag
        self._close_tag('/subroutineBody')

        return

    def compile_parameter_list(self):
        # opening tag
        self._write_tag('parameterList')

        # change indent
        self.indent_level += 1

        # write parameters
        ## TODO - suspect this is wrong, we need to look for , not type
        while self._check_is_type():
            token_type = self.tokenizer.token_type()
            self._write_tag(token_type, self.keyword_to_func[token_type]())
            if self._advance_and_check_type_only('IDENTIFIER'):
                self._write_tag('identifier', self.tokenizer.identifier())

        # close tag
        # TODO - parameter indent isn't working right
        self.indent_level -= 1

        # close
        self._write_tag(f'/parameterList')

        return

    def compile_var_dec(self):
        # opening tag
        self._write_tag('varDec')

        # rule - must be var
        if self._first_token_tag('KEYWORD', 'var'):
            self._write_tag('keyword', self.tokenizer.keyword())

        # rule - must be type
        self.tokenizer.advance()
        if self._check_is_type():
            token_type = self.tokenizer.token_type()
            self._write_tag(token_type.lower(), self.keyword_to_func[token_type]())
        else:
            raise Exception(f'Expected a type (see spec) but received {self.tokenizer.token_type()}')   

        # rule - must be varName
        if self._advance_and_check_type_only('IDENTIFIER'):
            self._write_tag('identifier', self.tokenizer.identifier())
        
        # rule - optional list of ', varName
        while self._advance_and_check_for_option('SYMBOL', ','):
            self._write_tag('symbol', ',')
            if self._advance_and_check_type_only('IDENTIFIER'):
                self._write_tag('identifier', self.tokenizer.identifier())

        # rule - must be ;
        if self._only_check('SYMBOL', ';'):
            self._write_tag('symbol', ';')

        # close tag
        self._close_tag('/varDec')

        return

    def compile_statements(self):
        # opening tag
        self._write_tag('Statements')
        self.indent_level += 1

        # rule - must be if, let, while, do or return
        while self.tokenizer.token_type() == 'KEYWORD' and self.tokenizer.keyword() in ('if', 'let', 'while', 'do', 'return'):
            # Dynamically get the method by name
            method = getattr(self, f'compile_{self.tokenizer.keyword()}')
            # Call the method
            method()
            

        # close tag - cannot use the func as we do not want to advance
        # decrement indent
        self.indent_level -= 1

        # close
        self._write_tag(f'/statements')

        return


    def compile_do(self):
        # opening tag
        self._write_tag('doStatement')

        # check first token
        if self._first_token_tag('KEYWORD', 'do'):
            self._write_tag('keyword', 'do')

        # call subroutine
        if self._advance_and_check_type_only('IDENTIFIER'):
            identifier = self.tokenizer.identifier()
            self.tokenizer.advance()
            current_symbol = self.tokenizer.symbol()
            if current_symbol in ('(', '.'):
                self._subroutine_call(current_symbol, identifier)
        
        if self._only_check('SYMBOL', ';'):
            self._write_tag('symbol', ';')

        # close tag
        self._close_tag('/doStatement')

        return
        

    def compile_let(self):
        # opening tag
        self._write_tag('letStatement')

        #  check first token
        if self._first_token_tag('KEYWORD', 'let'):
            self._write_tag('keyword', 'let')
        
        # rule - must be varName
        if self._advance_and_check_type_only('IDENTIFIER'):
            current_token = self.tokenizer.identifier()
            self._write_tag('identifier', current_token)
        
         # check for expression
        if self._advance_and_check_for_option('SYMBOL', '['):
            self._write_tag('symbol', '[')

            # rule - call expression
            self.tokenizer.advance()
            self.compile_expression()

            # rule - must be ']'
            if self._only_check('SYMBOL', ']'):
                self._write_tag('symbol', ']')
            
            # we need to advance to mirror case where 'check for expression' is false
            self.tokenizer.advance()
        
        # rule - must be '='
        current_token = self.tokenizer.symbol()
        if current_token == '=':
            self._write_tag('symbol', '=')
        
        else:
            raise Exception(f"Expected to receive '=' but received {current_token}")

        # rule - call expression
        self.tokenizer.advance()
        self.compile_expression()

        # rule - must be ';'
        if self._only_check('SYMBOL', ';'):
            self._write_tag('symbol', ';')

        # close
        self._close_tag('/letStatement')

        return 

    def compile_while(self):
        # opening tag
        self._write_tag('whileStatement')

        # check first token
        if self._first_token_tag('KEYWORD', 'while'):
            self._write_tag('keyword', 'while')
        
        # rule - must be '('
        if self._advance_and_check('SYMBOL', '('):
            self._write_tag('symbol', '(')
            
        # rule - call expression
        self.tokenizer.advance()
        self.compile_expression()

        # rule - must be ')'
        if self._only_check('SYMBOL', ')'):
            self._write_tag('symbol', ')')

        # rule - must be '{'
        if self._advance_and_check('SYMBOL', '{'):
            self._write_tag('symbol', '{')

        # rule - call statements
        self.tokenizer.advance()
        self.compile_statements()

        # rule - must be '}'
        if self._only_check('SYMBOL', '}'):
            self._write_tag('symbol', '}')

        # close
        self._close_tag('/whileStatement')

        return 
  

    def compile_return(self):
        # open  tag
        self._write_tag('returnStatement')

        # check first token
        if self._first_token_tag('KEYWORD', 'return'):
            self._write_tag('keyword','return')

        # check for expression
        if not self._advance_and_check_for_option('SYMBOL', ';'):
            self.compile_expression()
            if not self._only_check('SYMBOL', ';'):
                raise Exception("Expected to see ';'")
        
        self._write_tag('symbol', ';')

        # close tag
        self._close_tag('/returnStatement')

        return 


    def compile_if(self):
         # opening statement tag
        self._write_tag('ifStatement')

        ## MANDTORY IF CLAUSE

        # check current token
        if self._first_token_tag('KEYWORD', 'if'):
            self._write_tag('keyword', 'if')
        
        # rule - must be '('
        if self._advance_and_check('SYMBOL', '('):
            self._write_tag('symbol', '(')
            
        # rule - call expression
        self.tokenizer.advance()
        self.compile_expression()

        # rule - must be ')'
        if self._only_check('SYMBOL', ')'):
            self._write_tag('symbol', ')')

        # rule - must be '{'
        if self._advance_and_check('SYMBOL', '{'):
            self._write_tag('symbol', '{')

        # rule - call statements
        self.tokenizer.advance()
        self.compile_statements()

        # rule - must be '}'
        if self._only_check('SYMBOL', '}'):
            self._write_tag('symbol', '}')


        ## OPTIONAL ELSE CLAUSE

        # advance and check if we have an else statement
        if self._advance_and_check_for_option('KEYWORD', 'else'):
            self._write_tag('keyword', 'else')

            # rule - must be '{'
            if self._advance_and_check('SYMBOL', '{'):
                self._write_tag('symbol', '{')

            # rule - call statements
            self.tokenizer.advance()
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

        # opening statement tag
        self._write_tag('expression')
        self.indent_level += 1


        if self.tokenizer.symbol() == ')':
            return
        # rule - call term
        self.compile_term()

        # optional - is it an op?
        while self.tokenizer.symbol() in ('+', '-', '*', '/', '&', '|', '<', '>', '='):
            self._write_tag('symbol', self.tokenizer.symbol())
            self.tokenizer.advance()
            self.compile_term()

        
        
        self.indent_level -= 1
        self._write_tag('/expression')



    def compile_term(self):

        # open
        self._write_tag('term')
        self.indent_level +=1

        # determine type
        type_term  = self._type_term()

        if type_term == 'integerConstant':
            self._write_tag('integerConstant', self.tokenizer.int_val())
        elif type_term == 'stringConstant':
            self._write_tag('stringConstant', self.tokenizer.string_val())
        elif type_term == 'keywordConstant':
            self._write_tag('keywordConstant', self.tokenizer.keyword())
        # rule - ( expresion )
        elif type_term == 'expression':
            # rule - must be (
            self._write_tag('symbol', '(')
            # rule - must be an expression
            self.tokenizer.advance()
            self.compile_expression
            # rule - must be )
            if self._only_check('SYMBOL', ')'):
                self._write_tag('symbol', ')')
        elif type_term == 'unaryOp':
            self._write_tag('symbol', self.tokenizer.symbol())
            # could be varName, varName[expression] or subroutineCall
        elif type_term == 'identifier':
            # this means its either varName[expression] or subroutine
            identifier_token = self.tokenizer.identifier() # holding here so we have option of calling _compile_subroutine 
            self.tokenizer.advance()
            if self.tokenizer.token_type() == 'SYMBOL':
                current_symbol = self.tokenizer.symbol() # to avoid two calls
                # rule - varName [expression]
                if current_symbol == '[':
                    self._write_tag('identifier', identifier_token)
                    self._write_tag('symbol', '[')
                    # rule - must be an expression
                    self.tokenizer.advance()
                    self.compile_expression()
                    # rule - must be ]
                    if self._only_check('SYMBOL', ']'):
                        self._write_tag('symbol', ']')
                        self.tokenizer.advance()
                # rule - subroutineCall
                elif current_symbol in ('(', '.'):
                    self._subroutine_call(current_symbol, identifier_token)
                    # rule - must be ')'
                    
                
                # otherwise, it's varName only
                else:
                    self._write_tag('identifier', identifier_token)
                    self.indent_level -= 1
                    self._write_tag('/term')
                    return

            # otherwise, it's varName only
            else:
                self._write_tag('identifier', identifier_token)

            self.indent_level -= 1
            self._write_tag('/term')

            return
        
         # close tag
        self._close_tag('/term')
        return 


    def compile_expression_list(self):
        # open
        self._write_tag('expressionList')
        self.indent_level +=1

        # check for no expressions
        if not self.tokenizer.symbol() == ')':
           

            # rule - call expression
            self.compile_expression()

            # check for other expressions
            while self.tokenizer.symbol() == ',':
                self.tokenizer.advance()
                self.compile_expression()

                
        

        # close
        self.indent_level -=1
        self._write_tag('/expressionList')
        

        return




        #
    ### HELPER FUNCTIONS 
        #  
    def _write_tag(self, tag, content=None):
        indent = "  " * self.indent_level
        if content:
            self.file.write( f"{indent}<{tag}> {content} </{tag}>\n")
        else:
            self.file.write( f"{indent}<{tag}>\n")

    
    def _first_token_tag(self, keyword, content):
        # indent
        self.indent_level += 1
  

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
    
    def _only_check(self, keyword, content):
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
    
    def _advance_and_check_type_only(self, keyword):
         # get next token
        self.tokenizer.advance()

        # get token type    
        token_type = self.tokenizer.token_type()
        
        # check and return
        if token_type == keyword:
            return True
        else:
            raise Exception(f"Grammar error. Expected token of type '{token_type}' but receieved {keyword}")

    def _advance_and_check_for_option(self, keyword, content):
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
    
    # TODO refactor the below methods into one
    def _check_classVarDec(self,):
         # get token and type    
        current_token = self.tokenizer.keyword()
        token_type = self.tokenizer.token_type()

        if current_token in ('static', 'field') and token_type == 'KEYWORD':
            return True
        else:
            return False
    
    def _check_subroutineDec(self):
         # get token and type    
        current_token = self.tokenizer.keyword()
        token_type = self.tokenizer.token_type()

        if current_token in ('constructor', 'function', 'method') and token_type == 'KEYWORD':
            return True
        else:
            return False
    
    def _check_is_type(self):
        current_token = self.tokenizer.keyword()
        token_type = self.tokenizer.token_type()
        
        if (current_token in ('int', 'char', 'boolean') and token_type == 'KEYWORD') or (token_type == 'IDENTIFIER'):
            return True
        else:
            return False
        
    def _type_term(self):
        token_type = self.tokenizer.token_type()

        if token_type == 'INT_CONST':
            return 'integerConstant'
        if token_type == 'STRING_CONST':
            return 'stringConstant'
        if token_type == 'KEYWORD' and self.tokenizer.keyword() in ('true', 'false', 'null', 'this'):
            return 'keywordConstant'
        if token_type == 'IDENTIFIER':
            return 'identifier'
        if token_type == 'SYMBOL':
            symbol = self.tokenizer.symbol()
            if symbol == '(':
                return 'expression'
            if symbol in ('-', '~'):
                return 'unaryOp'
        else:
        
            raise Exception(f'Expected a term but first token was {token_type} and {self.tokenizer.symbol()}')
        
    
    def _subroutine_call(self, current_symbol, identifier_token):
        # subrule - optional grammar = subroutineName '(' expressionList ')' 
        if current_symbol == '(':
            self._write_tag('identifier', identifier_token)
            self._write_tag('symbol', '(')
            # rule - must be an expression
            self.tokenizer.advance()
            self.compile_expression_list()

        # subrule - optional grammar =  (className | varName) '.' subroutineName '(' expressionList ')'
        elif current_symbol == '.':
            self._write_tag('identifier', identifier_token)
            self._write_tag('symbol', '.')
            # rule - must be an identifier
            if self._advance_and_check_type_only('IDENTIFIER'):
                self._write_tag('identifier', self.tokenizer.identifier())
                if self._advance_and_check('SYMBOL', '('):
                    self._write_tag('symbol', '(')
                # rule - must be an expression
                self.tokenizer.advance()
                self.compile_expression_list()

        # rule - must be )
        if self._only_check('SYMBOL', ')'):
            self._write_tag('symbol', ')')
            self.tokenizer.advance()

        
    def _close_tag(self, content):
        # decrement indent
        self.indent_level -= 1

        # close
        self._write_tag(f'{content}')

        # advance and return
        self.tokenizer.advance()