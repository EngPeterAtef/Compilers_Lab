import graphviz
class GraphVisualize:
    def __init__(self):
        pass

    def graph_visualize(self,name="./graph_visualization.gv", json_data=None):
        try:
            if json_data is None:
                print("Error: No data to visualize")
                return False
            graph = graphviz.Digraph(engine='dot')
            
            for state, transitions in json_data.items():
                if state == 'startingState':
                    continue
                
                if transitions.get('isTerminatingState', False):
                    graph.node(state, shape='doublecircle')
                else:
                    graph.node(state, shape='circle')
                
                for char, next_state in transitions.items():
                    if char == 'isTerminatingState':
                        continue
                    graph.edge(state, next_state, label=char)
                    
            
            graph.render(name)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False