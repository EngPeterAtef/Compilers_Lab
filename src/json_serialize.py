class JsonSerialize:
    def __init__(self):
        pass
    def nfa_json_serialize(self,nfa):
        json_data = {}
        
        address_to_name = {}
        from_state = {}
        
        for _, state in enumerate(nfa.states):
            name = f"S{str(nfa.states.index(state))}"
            address_to_name[state] = name
            from_state[name] = []
        
        for transition in nfa.transitions:
            # Get the characters that are needed for the transition
            chars_str = []
            for char in transition.characters:
                if isinstance(char, tuple):
                    chars_str.append(f"({char[0]}-{char[1]})")
                else:
                    chars_str.append(char)
            chars_str = " | ".join(sorted(chars_str))
            
            # Get all the states that the transition goes to
            from_state[address_to_name[transition.from_]].append({"to": address_to_name[transition.to_], "char": chars_str})
        
        # Extracting starting state
        json_data["startingState"] = address_to_name[nfa.start]
        
        for _, state in enumerate(from_state):
            epsilons = 1
            json_data[state] = {
                "isTerminatingState": state == address_to_name[nfa.accept],
            }
            
            transitions = {}
            for transition in from_state[state]:
                if transition['char'] == 'epsilon':
                    transitions[f'epsilon{epsilons}'] = transition['to']
                    epsilons += 1
                else:
                    transitions[transition['char']] = transition['to']
            
            # Check if transitions is empty
            if len(transitions) > 0:
                json_data[state].update(transitions)
        
        return json_data
    def dfa_json_serialize(self,dfa):
        json_data = {}
        
        address_to_name = {}
        from_state = {}
        
        for _, state in enumerate(dfa.states):
            name = f"S{str(dfa.states.index(state))}"
            address_to_name[state] = name
            from_state[name] = []
        
        for transition in dfa.transitions:
            from_state[address_to_name[transition.from_]].append({"to": address_to_name[transition.to_], "char": transition.character})
        
        # Extracting starting state
        json_data["startingState"] = address_to_name[dfa.start]
        
        for _, state in enumerate(from_state):
            json_data[state] = {
                "isTerminatingState": state == address_to_name[dfa.accept],
            }
            
            transitions = {}
            for transition in from_state[state]:
                transitions[transition['char']] = transition['to']
            
            # Check if transitions is empty
            if len(transitions) > 0:
                json_data[state].update(transitions)
        
        return json_data
    def dfa_min_json_serialize(self,dfa_min):
        json_data = {}
        
        address_to_name = {}
        from_state = {}
        
        for _, state in enumerate(dfa_min.states):
            name = f"S{str(dfa_min.states.index(state))}"
            address_to_name[state] = name
            from_state[name] = []
        
        for transition in dfa_min.transitions:
            from_state[address_to_name[transition.from_]].append({"to": address_to_name[transition.to_], "char": transition.character})
        
        # Extracting starting state
        json_data["startingState"] = address_to_name[dfa_min.start]
        
        for _, state in enumerate(from_state):
            json_data[state] = {
                "isTerminatingState": state == address_to_name[dfa_min.accept],
            }
            
            transitions = {}
            for transition in from_state[state]:
                transitions[transition['char']] = transition['to']
            
            # Check if transitions is empty
            if len(transitions) > 0:
                json_data[state].update(transitions)
        
        return json_data