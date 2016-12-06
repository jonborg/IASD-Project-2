import sys

class PDDL:
    def __init__(self):
        self.nb_consts  = 0     # number of constants
        self.consts     = []    # list of constants
        self.init_state = []    # list of predicates composing the initial state
        self.goal_state = []    # list of predicates composing the goal state
        self.actions    = []    # list of possible actions
        self.dict       = []    # dictionary describing every possible predicate

    def add_action(self, action):
        self.actions.append(action)
    
    def add_dict_entry(self, dict):
        self.dict.append(dict)
    
    def count_consts(self, predicate):
        for c in predicate:
            if c.isupper() and c not in self.consts:
                self.consts.append(c)
                self.nb_consts += 1
    
    def create_dict(self, consts, predicates):
        for pred in predicates:
            nb_args = 0
            p = pred.split("(")
            pred_name = p[0]
            pred_args = []
            for c in p[1]:
                if c.isupper() and c not in pred_args:
                    pred_args.append(c)
                    nb_args += 1
            dict = dictionary(pred_name, pred_args)
            add_dict_entry(dict)
            
                    
    def hebrand_base(self):
        
        # count constants
        # assuming all constants appear in I and G, no constant solely in A
        for i in self.init_state:
            if i != "I":
                self.count_consts(i)
        for g in self.goal_state:
            if g != "G":
                self.count_consts(g)
        
        
        
                
	
    def show(self):
        print(' '.join(self.consts))
        print("I " + ' '.join(self.init_state))
        print("G " + ' '.join(self.init_state))
        for a in self.actions:
            print("A " + a.name)
            for p in list((a.precond)):
                print("\t: " + p)
            for e in list((a.effect)):
                print("\t-> " + e)

class dictionary:
    def __init__(self, pred_name, pred_args):
        self.nb_args = len(pred_args)
        self.pred_name = pred_name
        self.pred_args = pred_args


class action:
    def __init__(self, name, precond, effect):
        self.nb_args = 0
        self.name    = name
        self.precond = precond
        self.effect  = effect




def open_file(file):
    """reads input file"""

    pddl = PDDL()

    f = open(file)
    lines = f.readlines()

    for line in lines:
        words = list(line.split())
        if words[0] == 'I':
            pddl.init_state = words[1:]
        if words[0] == 'G':
            pddl.goal_state = words[1:]
        if words[0] == 'A':
            ind = 0
            # the symbol '->' separates preconditions from effects
            for i in range(len(words)): # search index of symbol '->'
                if words[i] == "->":
                    ind = i
                    break
            name = words[1]
            preconditions = words[3:ind]
            effects = words[ind+1:]
            new_action = action(name, preconditions, effects)
            pddl.add_action(new_action)

    f.close()
    return pddl

def main():
	
	pddl = open_file(sys.argv[1])
	pddl.show()

if __name__ == "__main__":
	main()
