import sys
import itertools

def get_letters(string):
    letters = []
    for i in string:
        if i.isalpha():
            leters.append(i)
    return letters

class PDDL:
    def __init__(self):
        self.nb_consts      = 0     # number of constants
        self.consts         = []    # list of constants
        self.nb_preds       = 0     # number of predicates
        self.predicates     = []    # list of predicates
        self.init_state     = []    # list of predicates composing the initial state
        self.goal_state     = []    # list of predicates composing the goal state
        self.actions        = []    # list of possible actions
        self.dict           = {}    # dictionary describing every possible predicate
        self.h_init_state   = []    # initial state in Hebrand base
        self.h_goal_state   = []    # goal state in Hebrand base
        self.h_actions      = []    # list of action schemas in Hebrand base
        self.sat_init_state = []    # initial state in SAT (using DIMACS notation)
        self.sat_goal_state = []    # goal state in SAT (using DIMACS notation)
        self.sat_actions    = []    # action schemas in SAT (using DIMACS notation)
        

    def add_action(self, action):
        self.actions.append(action)
        
    
    def add_dict_entry(self, dic):
        self.dict.append(dic)
        
    
    def count_consts(self, predicate):
        predicate=predicate[0:len(predicate)-1].split("(")
        predicate=predicate[1].split(",")
        for c in predicate:
            if  c not in self.consts:
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
            self.add_dict_entry(dict)
        
            
                    
    def hebrand_base(self):
        
        # count constants
        # assuming all constants appear in I and G, no constant solely in A
        for i in self.init_state:
            if i != "I":
                self.count_consts(i)
        for g in self.goal_state:
            if g != "G":
                self.count_consts(g)

        # now need to add predicates to the predicate list
        p_list=[]
        #print(self.init_state + self.goal_state)
        for pred in self.init_state + self.goal_state:
            p = pred.split("(")
            pred_name = p[0]
            nb_args = p[1].count(",")+1
            info=[pred_name, nb_args]
            if info in p_list:
                continue
            else:
                p_list.append(info)
            

        for pred_info in p_list:
            if pred_info[1]>1:
                combinations=list(itertools.permutations(self.consts,pred_info[1]))
            else:
                combinations=self.consts

            for listing in combinations:
                predicate=pred_info[0] + "("
                for i in range (pred_info[1]):
                    if i==pred_info[1]-1:
                        predicate += listing[i] + ")"
                    else:
                        predicate += listing[i] + ","
                self.predicates.append(predicate)
       
            
        # attribute a number (SAT variable) to each predicate
        for i,p in enumerate(self.predicates, start=1):
            self.dict[str(p)] = i

        # transform I and G into hebrand base
        for key in self.dict:
            if key in self.init_state:
                self.h_init_state.append(key)
            else:
                self.h_init_state.append("-"+key)
            if key in self.goal_state:
                self.h_goal_state.append(key)
            else:
                self.h_goal_state.append("-"+key)
        
        # transform action schemas into hebrand base
        for action in self.actions:
            action_name = action.name.split("(")
            action_args = get_letters(action_name[1])
            action_name = action_name[0]
            combinations = list(itertools.permutations(self.consts,action.nb_args))
            
            for listing in combinations:
                h_action_name += action_name + "(" + ','.join(listing) + ")"
                
                # convert preconditions into hebrand base
                h_precond = []
                for precond in action.precond:
                    dummy_precond = precond.split("(")
                    precond_name = dummy_precond[0]
                    precond_args = []
                    args = get_letters(dummy_precond[1])
                    for i in args:
                        for j in action_args:
                            if i==j:
                                precond_args.append(listing[action_args.index(j)])
                    h_precond.append(precond)
                    
                # convert effects in to hebrand base
                h_effects = []
                for effect in action.effect:
                    dummy_effect = effect.split("(")
                    effect_name = dummy_effect[0]
                    effect_args = []
                    args = get_letters(dummy_effect[1])
                    for i in args:
                        for j in action_args:
                            if i==j:
                                effect_args.append(listing[action_args.index(j)])
                    h_effect.append(effect)
                
                self.h_actions.append(action(h_action_name, h_preconf, h_effect))
            
            
        
        # transform I and G into SAT
        for i in self.h_init_state:
            if i[0] == "-":
                self.sat_init_state.append("-"+str(self.dict[i[1:]]))
            else:
                self.sat_init_state.append(str(self.dict[i]))
        for g in self.h_goal_state:
            if g[0] == "-":
                self.sat_goal_state.append("-"+str(self.dict[g[1:]]))
            else:
                self.sat_goal_state.append(str(self.dict[g]))
        
        

    def show(self):
        print("Constants: " + ' '.join(self.consts))
        print("I " + ' '.join(self.init_state))
        print("G " + ' '.join(self.goal_state))
        for a in self.actions:
            print("A " + a.name)
            for p in list((a.precond)):
                print("\t: " + p)
            for e in list((a.effect)):
                print("\t-> " + e)
        print("Predicates:")
        for d in self.predicates:
            print("\t" + d)
        print("Hebrand base:")
        print("\t " + "I " + ' '.join(self.h_init_state))
        print("\t " + "G " + ' '.join(self.h_goal_state))
        print("SAT formulation:")
        print("\t " + "I " + ' '.join(self.sat_init_state))
        print("\t " + "G " + ' '.join(self.sat_goal_state))
        print("SAT dictionary:")
        # invert mapping for printing
        inv_dict = dict((v,k) for k,v in self.dict.items())
        for key in sorted(inv_dict.keys()):
            print("\t" + str(key) + " : " + str(inv_dict[key]))
        
        

class dictionary:
    def __init__(self, pred_name, pred_args):
        self.nb_args = len(pred_args)
        self.pred_name = pred_name
        self.pred_args = pred_args


class action:
    def __init__(self, name, precond, effect):
        self.nb_args = name.count(',')+1
        self.name    = name
        self.precond = precond
        self.effect  = effect

    def show(self):
        print(self.nb_args)
        print(self.name)
        print(self.precond)
        print(self.effect)




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
    pddl.hebrand_base()
    pddl.show()

if __name__ == "__main__":
	main()
