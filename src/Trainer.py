import numpy as np

class Trainer():
    def __init__(self, args):

        self.verbose = args.verbose
        self.num_actions = args.num_actions
        self.s = 0
        self.a = 0
        self.q = np.random.rand(args.num_states, args.num_actions) * 2 - 1
        self.alpha = args.alpha
        self.gamma = args.gamma
        self.rar = args.rar
        self.radr = args.radr
        self.dyna = args.dyna

    def addEvidence(self):
        pass

    def query(self):
        pass

    def storeModel(self):
        pass