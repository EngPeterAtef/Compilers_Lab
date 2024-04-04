import re
from parser_classes import *
from graph_visualize import GraphVisualize
from json_serialize import JsonSerialize
import json


class State:
    pass


@dataclass
class Edge:
    from_: State
    to_: State
    characters: set  # of chars (literals, epsilon) and pairs of chars (for ranges)


@dataclass
class NFA:
    start: State
    accept: State

    # All states of the NFA including the start and accept
    states: list  # of State
    transitions: list  # of Edge


class NFA_CLASS:
    def __init__(self, regex):
        if not self.check_regex(regex):
            raise ValueError(f"Invalid regular expression: {regex}")

        self._regex = regex
        self._tokens = []
        self._ast = None
        self.nfa = None
        self.nfa_json = None

        self.tokenize()
        self.parse()
        self.AST_to_NFA()
        self.nfa_to_json()
        self.nfa_visualize()

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
            ".": TokenType.DOT,
        }
        escape = "\\"

        token_stream = []
        prev_char = None

        for char in self._regex:
            if char == escape:
                prev_char = char
                continue

            if char in character_map and prev_char != escape:
                token_stream.append(Token(character_map[char], char))
            else:
                token_stream.append(Token(TokenType.LITERAL, char))

            prev_char = char

        self._tokens = token_stream

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
        expression, _ = parse_regex(self._tokens, 0)
        self._ast = expression

    def construct_nfa(self, node):
        if isinstance(node, OrAstNode):
            return self.construct_or_nfa(node)
        elif isinstance(node, SeqAstNode):
            return self.construct_seq_nfa(node)
        elif isinstance(node, StarAstNode) or isinstance(node, PlusAstNode):
            return self.construct_star_plus_nfa(node)
        elif isinstance(node, QuestionMarkAstNode):
            return self.construct_question_mark_nfa(node)
        elif isinstance(node, LiteralCharacterAstNode) or isinstance(
            node, CharacterClassAstNode
        ):
            return self.construct_literal_character_class_nfa(node)

    def construct_or_nfa(self, node):
        # If we have regex A|B

        # Get the NFAs representing A and B
        left_nfa = self.construct_nfa(node.left)
        right_nfa = self.construct_nfa(node.right)

        # Create 2 new states, start and accept for the full NFA
        start = State()
        accept = State()

        # Link the start state with both the start of A's NFA and B's NFA with an epsilon transitions
        start_transition_1 = Edge(from_=start, to_=left_nfa.start, characters={EPSILON})
        start_transition_2 = Edge(
            from_=start, to_=right_nfa.start, characters={EPSILON}
        )

        # Link the accept state with both the accept of A's NFA and B's NFA with an epsilon transitions
        final_transition_1 = Edge(
            from_=left_nfa.accept, to_=accept, characters={EPSILON}
        )
        final_transition_2 = Edge(
            from_=right_nfa.accept, to_=accept, characters={EPSILON}
        )

        # Finalize the Or NFA and return it
        states = [*left_nfa.states, *right_nfa.states, start, accept]
        transitions = [
            *left_nfa.transitions,
            *right_nfa.transitions,
            start_transition_1,
            start_transition_2,
            final_transition_1,
            final_transition_2,
        ]
        return NFA(start, accept, states, transitions)

    def construct_seq_nfa(self, node):
        # If we have regex AB

        # Get the NFAs representing A and B
        left_nfa = self.construct_nfa(node.left)
        right_nfa = self.construct_nfa(node.right)

        # Link the two NFAs by connecting the accept state of A to the start state of B
        final_transition = Edge(
            from_=left_nfa.accept, to_=right_nfa.start, characters={EPSILON}
        )

        # Finalize the Seq NFA and return it
        states = [*left_nfa.states, *right_nfa.states]
        transitions = [*left_nfa.transitions, *right_nfa.transitions, final_transition]
        return NFA(left_nfa.start, right_nfa.accept, states, transitions)

    def construct_star_plus_nfa(self, node):
        # If we have regex A* or A+
        is_star = isinstance(node, StarAstNode)

        # Get the NFA representing A
        left_nfa = self.construct_nfa(node.left)

        # Create 2 new states, start and accept for the full NFA
        start = State()
        accept = State()

        # Link the new start to the start of A's NFA
        start_transition_1 = Edge(from_=start, to_=left_nfa.start, characters={EPSILON})

        # For star nodes only, it also goes to the accept state directly to represent accepting an empty inputs
        start_transition_2 = Edge(from_=start, to_=accept, characters={EPSILON})

        # Link the accept state with the accept of A's NFA
        final_transition_1 = Edge(
            from_=left_nfa.accept, to_=accept, characters={EPSILON}
        )

        # To represent zero|one 'or more' we link the accept state of A with the new start state
        final_transition_2 = Edge(
            from_=left_nfa.accept, to_=start, characters={EPSILON}
        )

        # Finalize the star or plus NFA and return it
        states = [*left_nfa.states, start, accept]
        transitions = [
            *left_nfa.transitions,
            start_transition_1,
            final_transition_1,
            final_transition_2,
        ]
        if is_star:
            transitions.append(start_transition_2)

        return NFA(start, accept, states, transitions)

    def construct_question_mark_nfa(self, node):
        # If we have regex A?

        # Get the NFA representing A
        left_nfa = self.construct_nfa(node.left)

        # Create 2 new states, start and accept for the full NFA
        start = State()
        accept = State()

        # Link the new start to the start of A's NFA
        start_transition_1 = Edge(from_=start, to_=left_nfa.start, characters={EPSILON})

        # It also goes to the accept state directly to represent accepting an empty inputs
        start_transition_2 = Edge(from_=start, to_=accept, characters={EPSILON})

        # Link the accept state with the accept of A's NFA
        final_transition_1 = Edge(
            from_=left_nfa.accept, to_=accept, characters={EPSILON}
        )

        # Finalize the question mark NFA and return it
        states = [*left_nfa.states, start, accept]
        transitions = [
            *left_nfa.transitions,
            start_transition_1,
            start_transition_2,
            final_transition_1,
        ]

        return NFA(start, accept, states, transitions)

    def construct_literal_character_class_nfa(self, node):
        # If we have regex 'x' for any character x or a character class [..]

        is_literal = isinstance(node, LiteralCharacterAstNode)
        chars = {node.char} if is_literal else node._class

        # Create 2 new states, start and accept for the full NFA
        start = State()
        accept = State()

        # Single transition that goes from the starting to the accepting on the relevant characters
        final_transition = Edge(start, accept, chars)

        # Finalize the literal and character class NFA and return it
        states = [start, accept]
        transitions = [final_transition]

        return NFA(start, accept, states, transitions)

    def AST_to_NFA(self):
        self.nfa = self.construct_nfa(self._ast)

    def nfa_to_json(self):
        """
        This function is used to convert the NFA to a JSON format
        """
        nfa = self.nfa
        json_serialize = JsonSerialize()
        self.nfa_json = json_serialize.nfa_json_serialize(nfa)
        del json_serialize
        # store the nfa json in a file
        with open("nfa.json", "w") as f:
            json.dump(self.nfa_json, f, indent=4)

    def nfa_visualize(self, path="./nfa.gv"):
        json_data = self.nfa_json
        graph_visualize = GraphVisualize()
        if graph_visualize.graph_visualize(path, json_data):
            print(f"Visualization of the NFA is saved in {path}")
        else:
            print("Error: Visualization failed")
        del graph_visualize


# regex = "[A-Za-z]+[0-9]*"
# regex = "ab*c+de?(f|g|h)|mr|n|[p-qs0-9]"
# regex = "ab"

# nfa = NFA_CLASS(regex)
# print(nfa.nfa)
# print(nfa.nfa_json)
