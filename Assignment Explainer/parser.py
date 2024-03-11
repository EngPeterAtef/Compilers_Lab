# -*- coding: utf-8 -*-
"""NfaFromRegex.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MBSYKn6uuKmEywu-LM1YAmosv8O0_eyR
"""

from enum import Enum,auto

class TokenType(Enum):
  OR = auto()
  STAR = auto()
  PLUS = auto()
  QUESTION_MARK = auto()
  OPEN_PAREN = auto()
  CLOSED_PAREN = auto()
  OPEN_SQ_BRACKET = auto()
  CLOSED_SQ_BRACKET = auto()
  DASH = auto()
  LITERAL = auto()

from dataclasses import dataclass

@dataclass
class Token:
  ttype: TokenType
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
class ZeroOrMoreAstNode(AstNode):
  left: AstNode
@dataclass
class OneOrMoreAstNode(AstNode):
  left: AstNode
@dataclass
class ZeroOrOneAstNode(AstNode):
  left: AstNode

@dataclass
class LiteralCharacterAstNode(AstNode):
  char: str

@dataclass
class CharacterClassAstNode(AstNode):
  clas: set #of strs and pairs

def parse_square_bracket_content(token_stream,curr_token):
  more_tokens_remaining = curr_token < len(token_stream)
  if not more_tokens_remaining:
    raise Exception()

  chars = []
  waiting_for_range_end = False

  while more_tokens_remaining \
  and   token_stream[curr_token].ttype != TokenType.CLOSED_SQ_BRACKET:

      if token_stream[curr_token].ttype == TokenType.DASH:
          waiting_for_range_end = True
      elif waiting_for_range_end:
          if len(chars) == 0:
            raise Exception()

          range_start = chars.pop()
          range_end = token_stream[curr_token].string 
          chars.push((range_start,range_end))
      else:
          chars.append(token_stream[curr_token].string)
      
      curr_token = curr_token + 1
      more_tokens_remaining = curr_token < len(token_stream)
  
  if waiting_for_range_end: raise Exception()

  return CharacterClassAstNode(set(chars)),curr_token

def parse_base(token_stream,curr_token):
  more_tokens_remaining = curr_token < len(token_stream)
  if not more_tokens_remaining:
    raise Exception()
  
  tok = token_stream[curr_token]
  curr_token = curr_token + 1

  if tok.ttype == TokenType.LITERAL: 
    return LiteralCharacterAstNode(tok.string),curr_token

  if tok.ttype == TokenType.OPEN_PAREN:
    expr,curr_token = parse_regex(token_stream,curr_token)

    more_tokens_remaining = curr_token < len(token_stream)
    if not more_tokens_remaining:
      raise Exception()
    if token_stream[curr_token].ttype != TokenType.CLOSED_PAREN:
      raise Exception()
    
    curr_token = curr_token + 1
    return expr,curr_token
  
  if tok.ttype == TokenType.OPEN_SQ_BRACKET:
    sq_bracket,curr_token = parse_square_bracket_content(token_stream,curr_token)

    more_tokens_remaining = curr_token < len(token_stream)
    if not more_tokens_remaining:
      raise Exception()
    if token_stream[curr_token].ttype != TokenType.CLOSED_SQ_BRACKET:
      raise Exception()
    
    curr_token = curr_token + 1
    return sq_bracket,curr_token



def parse_quantified(token_stream,curr_token):
  left,curr_token = parse_base(token_stream,curr_token)

  more_tokens_remaining = curr_token < len(token_stream)
  if not more_tokens_remaining:
    return left,curr_token

  if token_stream[curr_token].ttype == TokenType.STAR:
    curr_token = curr_token + 1
    return ZeroOrMoreAstNode(left),curr_token

  if token_stream[curr_token].ttype == TokenType.PLUS:
    curr_token = curr_token + 1
    return OneOrMoreAstNode(left),curr_token
    
  if token_stream[curr_token].ttype == TokenType.QUESTION_MARK: 
    curr_token = curr_token + 1
    return ZeroOrOneAstNode(left),curr_token

  return left,curr_token

def parse_seq(token_stream,curr_token):
  left,curr_token = parse_quantified(token_stream,curr_token)

  more_tokens_remaining = curr_token < len(token_stream)
  if not more_tokens_remaining:
    return left,curr_token
  
  seq_expr = left
  while more_tokens_remaining \
  and   token_stream[curr_token].ttype != TokenType.OR \
  and   token_stream[curr_token].ttype != TokenType.CLOSED_PAREN:
      right,curr_token = parse_quantified(token_stream,curr_token)

      seq_expr = SeqAstNode(left= seq_expr,
                            right= right)
      
      more_tokens_remaining = curr_token < len(token_stream)

  return seq_expr,curr_token


def parse_or(token_stream,curr_token):
  left,curr_token = parse_seq(token_stream,curr_token)

  more_tokens_remaining = curr_token < len(token_stream)
  if not more_tokens_remaining:
    return left, curr_token
  
  or_expr = left
  while more_tokens_remaining \
  and   token_stream[curr_token].ttype == TokenType.OR:
      curr_token = curr_token + 1

      right,curr_token = parse_seq(token_stream,curr_token)

      or_expr = OrAstNode(left= or_expr,
                          right= right)

      more_tokens_remaining = curr_token < len(token_stream)
  
  return or_expr, curr_token 

def parse_regex(token_stream,curr_token):
  return parse_or(token_stream,curr_token)

def parse(token_stream):
  expr,_ = parse_regex(token_stream,0)
  return expr

#ab*c+de?(f|g|h)|mr|n|[pq]
toks = [
    Token(TokenType.LITERAL,"a"),
    Token(TokenType.LITERAL,"b"),
    Token(TokenType.STAR,"*"),
    Token(TokenType.LITERAL,"c"),
    Token(TokenType.PLUS,"+"),
    Token(TokenType.LITERAL,"d"),
    Token(TokenType.LITERAL,"e"),
    Token(TokenType.QUESTION_MARK,"?"),

    Token(TokenType.OPEN_PAREN,"("),
    Token(TokenType.LITERAL,"f"),
    Token(TokenType.OR,"|"),
    Token(TokenType.LITERAL,"g"),
    Token(TokenType.OR,"|"),
    Token(TokenType.LITERAL,"h"),
    Token(TokenType.CLOSED_PAREN,")"),

    Token(TokenType.OR,"|"),
    Token(TokenType.LITERAL,"m"),
    Token(TokenType.LITERAL,"r"),

    Token(TokenType.OR,"|"),
    Token(TokenType.LITERAL,"n"),

    Token(TokenType.OPEN_SQ_BRACKET,"["),
    Token(TokenType.LITERAL,"p"),
    Token(TokenType.LITERAL,"q"),
    Token(TokenType.CLOSED_SQ_BRACKET,"]")
]
print(parse(toks))