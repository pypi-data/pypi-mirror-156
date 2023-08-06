import numpy as np
from sklearn.neural_network import MLPClassifier

class drl():
    def __init__(self, observations, actions, learning_rate=0.1, discount=0.8, epsilon=0.2, zeros=True):
        self.observations = observations
        self.actions = actions
        self.learning_rate = learning_rate
        self.discount = discount
        self.epsilon = epsilon

        self.clf = MLPClassifier(hidden_layer_sizes=(20,20), random_state=34, solver='adam', max_iter=1)

    def setEpsilon(self, epsilon):
        self.epsilon = epsilon

    def selectActionWithExploration(self):
        if np.random.random() > self.epsilon:
            action = self.clf.predict([self.state])[0]
        else:
            action = np.random.randint(0, self.actions)
        return action

    def selectAction(self):
        action = np.argmax(self.Q[self.state])
        return action

    def updateState(self, state):
        self.state = state

    def update(self, action, newState, reward):
        self.clf.fit([self.state],[action])
        self.state = newState
