import sys

class PDDL:
    def __init__(self):
        self.init_state = []
        self.goal_state = []
        self.actions    = []

    def add_action(self, id, action):
        self.actions.append(action)
	
    def show(self):
        print("I " + ' '.join(self.init_state))
        print("G " + ' '.join(self.init_state))
        for a in self.actions:
            print("A " + a.name)
            for p in list((a.precond)):
                print("\t: " + p)
            for e in list((a.effect)):
                print("\t-> " + e)



class action:
    def __init__(self, name, precond, effect):
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
            pddl.add_action(new_action.name, new_action)

    f.close()
    return pddl

def main():
	
	pddl = open_file(sys.argv[1])
	pddl.show()

if __name__ == "__main__":
	main()
	