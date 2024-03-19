from enum import Enum, auto
from dataclasses import dataclass

EPSILON = 'epsilon'

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

class AstNode:
    pass

@dataclass
class OrAstNode(AstNode):
    left: AstNode
    right: AstNode

@dataclass
class SeqAstNode(AstNode):
    left: AstNode
    right: AstNode

@dataclass
class StarAstNode(AstNode):
    left: AstNode

@dataclass
class PlusAstNode(AstNode):
    left: AstNode

@dataclass
class QuestionMarkAstNode(AstNode):
    left: AstNode

@dataclass
class LiteralCharacterAstNode(AstNode):
    char: str

@dataclass
class CharacterClassAstNode(AstNode):
    _class: set # of strs and pairs


def parse_regex(tokens, current_token):
    """
    regex-expression -> or-expression
    """
    return parse_or(tokens, current_token)

def parse_or(tokens, current_token):
    """
    or-expression -> sequence-expression (OR sequence-expression)*
    """
    # Get the left sequence expression
    left, current_token = parse_sequence(tokens, current_token)
    
    # Check if there are no more tokens
    if current_token >= len(tokens):
        return left, current_token
    
    # Final AST node
    or_expression = left
    
    # Loop through the rest of the tokens
    while current_token < len(tokens) and tokens[current_token].token_type == TokenType.OR:
        current_token += 1
        
        # Get the right sequence expression
        right, current_token = parse_sequence(tokens, current_token)
        
        or_expression = OrAstNode(left=or_expression, right=right)
    
    return or_expression, current_token

def parse_sequence(tokens, current_token):
    """
    sequence-expression -> quantified-expression (quantified-expression)*
    """
    # Get the left quantified expression
    left, current_token = parse_quantified(tokens, current_token)
    
    # Check if there are no more tokens
    if current_token >= len(tokens):
        return left, current_token
    
    # Final AST node
    sequence_expression = left
    
    # Loop through the rest of the tokens
    while current_token < len(tokens) \
        and tokens[current_token].token_type != TokenType.OR \
        and tokens[current_token].token_type != TokenType.CLOSED_PAREN:
        
        right, current_token = parse_quantified(tokens, current_token)
        
        sequence_expression = SeqAstNode(left=sequence_expression, right=right)
    
    return sequence_expression, current_token

def parse_quantified(tokens, current_token):
    """
    quantified-expression -> base-expression (STAR | PLUS | QUESTION_MARK)?
    """
    # Get the left base expression
    left, current_token = parse_base(tokens, current_token)
    
    # Check if there are no more tokens
    if current_token >= len(tokens):
        return left, current_token
    
    if tokens[current_token].token_type == TokenType.STAR:
        current_token += 1
        return StarAstNode(left=left), current_token
    
    if tokens[current_token].token_type == TokenType.PLUS:
        current_token += 1
        return PlusAstNode(left=left), current_token
    
    if tokens[current_token].token_type == TokenType.QUESTION_MARK:
        current_token += 1
        return QuestionMarkAstNode(left=left), current_token
    
    return left, current_token

def parse_base(tokens, current_token):
    """
    base-expression -> LITERAL
                    | DOT
                    | OPEN_PAREN regex-expression CLOSED_PAREN
                    | OPEN_SQ_BRACKET sq-bracket-content CLOSED_SQ_BRACKET
    """
    # Check if there are no more tokens
    if current_token >= len(tokens):
        raise Exception("No more tokens to parse")
    
    token = tokens[current_token]
    current_token += 1
    
    if token.token_type == TokenType.LITERAL:
        return LiteralCharacterAstNode(char=token.string), current_token
    
    if token.token_type == TokenType.DOT:
        # Epsilon because dot match any character
        return LiteralCharacterAstNode(char='.'), current_token
    
    if token.token_type == TokenType.OPEN_PAREN:
        expression, current_token = parse_regex(tokens, current_token)
        
        if current_token >= len(tokens):
            raise Exception("No more tokens to parse")
        
        if tokens[current_token].token_type != TokenType.CLOSED_PAREN:
            raise Exception("Expected closed parenthesis")
        
        current_token += 1
        return expression, current_token
    
    if token.token_type == TokenType.OPEN_SQ_BRACKET:
        sq_bracket, current_token = parse_sq_bracket_content(tokens, current_token)
        
        if current_token >= len(tokens):
            raise Exception("No more tokens to parse")
        
        if tokens[current_token].token_type != TokenType.CLOSED_SQ_BRACKET:
            raise Exception("Expected square bracket")
        
        current_token += 1
        return sq_bracket, current_token

def parse_sq_bracket_content(tokens, current_token):
    """
    sq-bracket-content -> LITERAL
                        | LITERAL DASH LITERAL
    """
    # Check if there are no more tokens
    if current_token >= len(tokens):
        raise Exception("No more tokens to parse")
    
    chars = []
    is_dash_reached = False
    
    while current_token < len(tokens) \
        and tokens[current_token].token_type != TokenType.CLOSED_SQ_BRACKET:
        
        if tokens[current_token].token_type == TokenType.DASH:
            is_dash_reached = True
        elif is_dash_reached:
            if len(chars) == 0:
                raise Exception("Expected at least one character")
            
            range_start = chars.pop()
            range_end = tokens[current_token].string
            chars.append((range_start, range_end))
            is_dash_reached = False
        else:
            chars.append(tokens[current_token].string)
        
        current_token += 1
    
    if is_dash_reached:
        raise Exception("Wrong range format")
    
    return CharacterClassAstNode(set(chars)), current_token