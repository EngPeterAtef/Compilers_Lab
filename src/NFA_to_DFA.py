from graph_visualize import GraphVisualize
from json_serialize import JsonSerialize
from parser_classes import *
import json


@dataclass
class DfaState:
    name: str = None

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class DfaEdge:
    from_: DfaState
    to_: DfaState
    characters: set  # of chars (literals, epsilon) and pairs of chars (for ranges)


@dataclass
class DFA:
    start: DfaState
    accept: list  # list of accepting states
    non_accept: list  # list of non accepting states
    # All states of the DFA including the start and accept
    states: list  # of State
    transitions: list  # of Edge


class DFA_CLASS:
    def __init__(self, dfa=None, inputs=[]):
        """_summary_
        class that contains the methods to convert NFA to DFA
        dfa: DFA object
        inputs: list of inputs of the NFA
        """
        self._dfa = dfa
        self.inputs = inputs

    def epsilon_closure(self, nfa, state):
        """_summary_
        This function is used to get the epsilon closure of a given state
        Args:
            nfa (NFA): this a NFA object contains the NFA data
            state (State): this is the state that we want to get the epsilon closure for

        Returns:
            set: closure set of states that are reachable from the given state using epsilon transitions
        """
        closure = set()
        # add the state to its closure set
        closure.add(state)
        for edge in nfa.transitions:
            if edge.from_ == state and EPSILON in edge.characters:
                # add the state that is reachable using epsilon transition to the closure set
                closure.add(edge.to_)
                # call the function recursively to get the epsilon closure of the next state
                closure = closure.union(self.epsilon_closure(nfa, edge.to_))
        return closure

    def move(self, transitions, states, character):
        """_summary_
        This function is used to get the move of a given set of states using a given character
        Args:
            transitions (List): list of transitions of the NFA (list of edges)
            states (set): set of states that we want to get the move for. states list is a subset of nfa.states because we apply the input on only a subset
            character (str): the character that we want to move to

        Returns:
            set: set of states that are reachable from the given states using the given character
        """
        move = set()
        for state in states:
            for edge in transitions:
                if edge.from_ == state and character in edge.characters:
                    move.add(edge.to_)
        return move

    def subset_construction(self, nfa, inputs):
        """_summary_
        This function is used to convert NFA to DFA using the subset construction algorithm
        Args:
            nfa (NFA): this a NFA object contains the NFA data
            inputs (list): list of inputs of the NFA
        """
        # get the epsilon closure of the start state
        start_set = self.epsilon_closure(nfa, nfa.start)
        # get the inputs of the NFA
        self.inputs = inputs
        # list of transitions of the DFA
        transitions = []
        # list of states of the DFA
        states = []
        # add the start state to the list of states of the DFA
        states.append(start_set)
        # list of accepting states of the DFA
        accept = []
        # list of non accepting states of the DFA
        non_accept = []
        # list of states that we need to visit
        to_visit = [start_set]
        # while there are states to visit
        while to_visit:
            # get the first state in the list of states to visit
            current_state = to_visit.pop(0)
            # for each input in the inputs list
            for input_ in self.inputs:
                # get the move of the current state using the input
                move = self.move(nfa.transitions, current_state, input_)
                # get the epsilon closure of the move set
                for state in move:
                    move = move.union(self.epsilon_closure(nfa, state))
                # if the move set is not empty
                if move:
                    # add the move set to the list of states of the DFA
                    if move not in states:
                        states.append(move)
                        to_visit.append(move)
                    # add the transition from the current state to the move set using the input
                    transitions.append(
                        DfaEdge(from_=current_state, to_=move, characters={input_})
                    )

        # we need to convert every set of states to a state object
        for i, state in enumerate(states):
            temp = state
            states[i] = DfaState(name=",".join([state.name for state in state]))
            # loop over the transitions to update the from_ and to_ states
            for transition in transitions:
                if transition.from_ == temp:
                    transition.from_ = states[i]
                if transition.to_ == temp:
                    transition.to_ = states[i]
            # if the state contains an accepting state of the NFA
            if temp.intersection({nfa.accept}):
                # add the state to the list of accepting states of the DFA
                accept.append(states[i])
            else:
                # add the state to the list of non accepting states of the DFA
                non_accept.append(states[i])
        # create a DFA object
        self._dfa = DFA(
            start=states[0],
            accept=accept,
            non_accept=non_accept,
            states=states,
            transitions=transitions,
        )

    def print_dfa(self):
        """
        This function is used to print the DFA object
        """
        print("Start State: ", self._dfa.start.name)
        print("Accepting States: ", [state.name for state in self._dfa.accept])
        print("Non Accepting States: ", [state.name for state in self._dfa.non_accept])
        print("States: ", [state.name for state in self._dfa.states])
        print("Transitions: ")
        for transition in self._dfa.transitions:
            print(
                f"From: {transition.from_.name}, To: {transition.to_.name}, Characters: {transition.characters}"
            )

    def rename_dfa_states(self):
        """
        This function is used to rename the states of the DFA to S0, S1, S2, ...
        """
        for i, state in enumerate(self._dfa.states):
            state.name = f"S{i}"

    def dfa_to_json(self, file_path: str):
        """
        This function is used to convert the DFA to a JSON format (serialize the DFA object)
        Args:
            file_path (str): the path of the file that we want to store the JSON data in
        Returns:
            None: no return value
        """
        json_serialize = JsonSerialize()
        self.dfa_json = json_serialize.dfa_json_serialize(self._dfa)
        del json_serialize
        # store the dfa json in a file
        with open(file_path, "w") as f:
            json.dump(self.dfa_json, f, indent=4)

    def visualize_dfa(self, path="./dfa"):
        """_summary_
        Args:
            path (str, optional): Path where the gv file will be stores. Defaults to "./dfa.gv".
        """
        graph_visualize = GraphVisualize()
        if graph_visualize.graph_visualize(path, self.dfa_json):
            print(f"Visualization of the DFA is saved in {path}")
        else:
            print("Error: Visualization DFA failed")
        del graph_visualize

    def minimize_dfa(self, inputs) -> DFA:
        """_summary_
        This function is used to minimize the DFA
        Args:
            inputs (list): list of inputs of the NFA (Terminals in Regex)
        Returns:
            DFA: minimized DFA object
        """
        # the current state of the DFA
        pi = []
        # list of accepting states of the DFA
        accept = self._dfa.accept
        if accept:
            # add the accepting states to the current state of the DFA
            pi.append(set(accept))
        # list of non accepting states of the DFA
        non_accept = self._dfa.non_accept
        if non_accept:
            # add the non accepting states to the current state of the DFA
            pi.append(set(non_accept))
        print("Initial Partition: ", pi)
        # flag to tell if there is a change in the partition
        change = True
        while change:
            change = False
            # create a new partition
            new_pi = []
            for group in pi:
                if len(group) > 1:
                    # the splited states in the group
                    # key is the transition table for the state
                    splitted_states = {}
                    for state in group:
                        # transion table for each state
                        state_transition_table = {}
                        for input_ in inputs:
                            for transition in self._dfa.transitions:
                                if (
                                    transition.from_ == state
                                    and input_ in transition.characters
                                ):
                                    if input_ not in state_transition_table:
                                        state_transition_table[input_] = set()
                                    state_transition_table[input_].add(transition.to_)
                        str_temp = str(state_transition_table)
                        print("Transition Table: ", str_temp)
                        if str_temp not in splitted_states:
                            splitted_states[str_temp] = set()
                        splitted_states[str_temp].add(state)
                    # print("Splitted States: ", splitted_states)
                    # if there is more than one transition table for the group
                    if len(splitted_states) > 1:
                        # change is True to check on the new partitions
                        change = True
                        print("Splitted States: ", splitted_states)
                        # add the splited states to the new partition
                        for value in splitted_states.values():
                            new_pi.append(set(value))
                    else:
                        # if there is only one transition table for the group
                        # add the group to the new partition
                        new_pi.append(group)
                else:
                    # if the group contains only one state
                    # add the group to the new partition
                    new_pi.append(group)
            # if there is a change in the partition
            if change:
                pi = new_pi
                # print("New Partition: ", pi)
        # list of states of the minimized DFA
        min_states = []
        # list of transitions of the minimized DFA
        min_transitions = []
        # list of accepting states of the minimized DFA
        min_accept = []
        # list of non accepting states of the minimized DFA
        min_non_accept = []
        # start state of the minimized DFA
        start = None
        print("Final Partition: ", pi)
        # create the state sof the minimized DFA
        for i, group in enumerate(pi):
            state = DfaState(name=f"S{i}")
            min_states.append(state)
            if group.intersection(self._dfa.accept):
                min_accept.append(state)
            else:
                min_non_accept.append(state)
            # get the start state of the minimized DFA
            if self._dfa.start in group:
                start = state
        # create the transitions of the minimized DFA
        for transition in self._dfa.transitions:
            for i, group in enumerate(pi):
                if transition.from_ in group:
                    from_ = min_states[i]
                if transition.to_ in group:
                    to_ = min_states[i]
            min_transitions.append(
                DfaEdge(from_=from_, to_=to_, characters=transition.characters)
            )
        # create a DFA object for the minimized DFA
        minimized_dfa = DFA(
            start=start,
            accept=min_accept,
            non_accept=min_non_accept,
            states=min_states,
            transitions=min_transitions,
        )
        return minimized_dfa
