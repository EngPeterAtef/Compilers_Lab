import re
from parser_classes import *

class NFA():
    def __init__(self, regex):
        if not self.check_regex(regex):
            raise ValueError(f"Invalid regular expression: {regex}")
        
        self.regex = regex
        self.tokens = []
        self.expression = None
    
    def check_regex(self, regex):
        """
        Function used to check if the regex is valid or not
        """
        try:
            re.compile(regex)
        except re.error:
            print(f"Invalid regular expression: {regex}")
            return False
        return True
    
    def tokenize(self):
        """
        Function used to tokenize the regex, and handle the escape char '\'
        that helps us to escape the special characters in regex | * + ? ( ) [ ] - .
        """
        character_map = {
            "|": TokenType.OR,
            "*": TokenType.STAR,
            "+": TokenType.PLUS,
            "?": TokenType.QUESTION_MARK,
            "(": TokenType.OPEN_PAREN,
            ")": TokenType.CLOSED_PAREN,
            "[": TokenType.OPEN_SQ_BRACKET,
            "]": TokenType.CLOSED_SQ_BRACKET,
            "-": TokenType.DASH,
            ".": TokenType.DOT
        }
        escape = '\\'
        
        token_stream = []
        prev_char = None
        
        for char in self.regex:
            if char == escape:
                prev_char = char
                continue
            
            if char in character_map and prev_char != escape:
                token_stream.append(Token(character_map[char], char))
            else:
                token_stream.append(Token(TokenType.LITERAL, char))

            prev_char = char
        
        self.tokens = token_stream
    
    def parse(self):
        """
        Function used to create the Abstract Syntax Tree (AST) of the regex using the following grammar
        
        regex-expression        -> or-expression
        or-expression           -> sequence-expression (OR sequence-expression)*
        sequence-expression     -> quantified-expression (quantified-expression)*
        quantified-expression   -> base-expression (STAR | PLUS | QUESTION_MARK)?
        base-expression         -> LITERAL
                                | DOT
                                | OPEN_PAREN regex-expression CLOSED_PAREN
                                | OPEN_SQ_BRACKET sq-bracket-content CLOSED_SQ_BRACKET
        sq-bracket-content      -> LITERAL
                                | LITERAL DASH LITERAL
        """
        expression, _ = parse_regex(self.tokens, 0)
        self.expression = expression
    
    
    def AST_to_NFA(self):
        pass

regex = "[A-Za-z]+[0-9]*"
# regex = "ab*c+de?(f|g|h)|mr|n|[p-qs0-9]"

nfa = NFA(regex)
nfa.tokenize()
nfa.parse()

# print(nfa.tokens)
print(nfa.expression)