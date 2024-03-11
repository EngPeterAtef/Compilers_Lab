import re
from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    OR = auto()                 # |
    STAR = auto()               # *
    PLUS = auto()               # +
    QUESTION_MARK = auto()      # ?
    OPEN_PAREN = auto()         # (
    CLOSED_PAREN = auto()       # )
    OPEN_SQ_BRACKET = auto()    # [
    CLOSED_SQ_BRACKET = auto()  # ]
    DASH = auto()               # -
    LITERAL = auto()            # a-z A-Z 0-9
    DOT = auto()                # .

@dataclass
class Token:
    token_type: TokenType
    string: str

class NFA():
    def __init__(self, regex):
        if not self.check_regex(regex):
            raise ValueError(f"Invalid regular expression: {regex}")
        
        self.regex = regex
        self.tokens = []
    
    def check_regex(self, regex):
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
    
    def regex_to_NFA(self):
        pass


regex = "a()"
nfa = NFA(regex)
nfa.tokenize()
print(nfa.tokens)