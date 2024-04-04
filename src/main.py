from regex_to_NFA import NFA_CLASS
import json


def main():
    # regex = "[A-Za-z]+[0-9]*"
    # regex = "ab*c+de?(f|g|h)|mr|n|[p-qs0-9]"
    # regex = "ab"
    regex = "[AB]+"
    nfa = NFA_CLASS(regex)
    # get the json representation of the NFA
    nfa_json = nfa.get_nfa_json()
    # store the nfa json in a file
    with open("nfa.json", "w") as f:
        json.dump(nfa_json, f, indent=4)


if __name__ == "__main__":
    main()
