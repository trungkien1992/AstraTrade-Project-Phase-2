class Environment:
    def __init__(self, knowledge_hypergraph):
        self.knowledge_hypergraph = knowledge_hypergraph
        self.state = None

    def reset(self, question):
        self.state = {"question": question, "history": []}
        return self.state

    def step(self, action):
        action_type = action.get('type')
        action_content = action.get('content')

        reward = 0
        done = False

        if action_type == 'query':
            retrieved_knowledge = self._retrieve(action_content)
            self.state['history'].append(('query', action_content, retrieved_knowledge))
        elif action_type == 'answer':
            reward = 1
            done = True
            self.state['history'].append(('answer', action_content))

        return self.state, reward, done

    def _retrieve(self, query):
        # SIMULATED retrieval: return a hardcoded value
        return "Cairo"
