class JsonSerialize:
    def __init__(self):
        pass

    def nfa_json_serialize(self, nfa):
        """_summary_

        Args:
            nfa (NFA): The NFA data object

        Returns:
            dict: dictionary of the json data
        """
        json_data = {}

        address_to_name = {}
        from_state = {}

        for _, state in enumerate(nfa.states):
            name = f"S{str(nfa.states.index(state))}"
            address_to_name[state] = name
            from_state[name] = []

        for transition in nfa.transitions:
            # Get all the states that the transition goes to
            from_state[address_to_name[transition.from_]].append(
                {"to": address_to_name[transition.to_], "char": transition.characters}
            )

        # Extracting starting state
        json_data["startingState"] = address_to_name[nfa.start]

        for _, state in enumerate(from_state):
            epsilons = 1
            json_data[state] = {
                "isTerminatingState": state == address_to_name[nfa.accept],
            }

            transitions = {}
            for transition in from_state[state]:
                if transition["char"] == "epsilon":
                    transitions[f"epsilon{epsilons}"] = transition["to"]
                    epsilons += 1
                else:
                    transitions[transition["char"]] = transition["to"]

            # Check if transitions is empty
            if len(transitions) > 0:
                json_data[state].update(transitions)

        return json_data

    def dfa_json_serialize(self, dfa):
        """_summary_
        This function is used to serialize the DFA object to JSON format
        Args:
            dfa (DFA): the DFA data object
        Returns:
            dict: dictionary of the json data
        """
        json_data = {}
        # set the starting state in the json data
        json_data["startingState"] = dfa.start.name

        # loop over the states in the DFA
        for _, state in enumerate(dfa.states):
            # loop over the transitions in the state
            json_data[state.name] = {
                "isTerminatingState": state in dfa.accept,
            }
            for transition in dfa.transitions:
                if transition.from_ == state:
                    json_data[state.name][
                        "".join(list(transition.characters))
                    ] = transition.to_.name
        return json_data

    def dfa_min_json_serialize(self, dfa_min):
        json_data = {}
