import sys
import itertools
import copy

def get_letters(string):
    letters = []
    for i in string:
        if i.isalpha():
            letters.append(i)
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
        self.sat_sentence   = []
        self.dimacs_sentence = ""
        self.dimacs2hebrand_dict = {}
        

    def add_action(self, action):
        self.actions.append(action)
        
    
    def count_consts(self, predicate):
        predicate=predicate[0:len(predicate)-1].split("(")
        predicate=predicate[1].split(",")
        for c in predicate:
            if  c not in self.consts:
                self.consts.append(c)
                self.nb_consts += 1
        
            
                    
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
                    if pred_info[1]>1:
                        if i==pred_info[1]-1:
                            predicate += listing[i] + ")"
                        else:
                            predicate += listing[i] + ","
                    else:
                        if i==pred_info[1]-1:
                            predicate += listing + ")"
                        else:
                            predicate += listing + ","
                self.predicates.append(predicate)
       
            
        # attribute a number (SAT variable) to each predicate
        # i.e., build predicate dictionary
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
        for act in self.actions:
            action_name = act.name.split("(")
            action_args = get_letters(action_name[1])
            action_name = action_name[0]
            combinations = list(itertools.permutations(self.consts,act.nb_args))
            
            for listing in combinations:
                h_action_name = action_name + "(" + ','.join(listing) + ")"
                
                # convert preconditions into hebrand base
                h_precond = []
                for precond in act.precond:
                    dummy_precond = precond.split("(")
                    precond_name = dummy_precond[0]
                    precond_args = []
                    args = get_letters(dummy_precond[1])
                    for i in args:
                        for j in action_args:
                            if i==j:
                                precond_args.append(listing[action_args.index(j)])
                    h_precond.append(precond_name+"("+','.join(precond_args)+")")
                    
                # convert effects in to hebrand base
                h_effects = []
                for effect in act.effect:
                    dummy_effect = effect.split("(")
                    effect_name = dummy_effect[0]
                    effect_args = []
                    args = get_letters(dummy_effect[1])
                    for i in args:
                        for j in action_args:
                            if i==j:
                                effect_args.append(listing[action_args.index(j)])
                    h_effects.append(effect_name+"("+','.join(effect_args)+")")
                
                self.h_actions.append(action(h_action_name, h_precond, h_effects))
        
        
        # update predicate dictionary with grounded actions
        last_val = sorted(self.dict.values())[-1]
        for a in self.h_actions:
            last_val += 1
            self.dict[a.name] = last_val
            
        
    def hebrand2sat(self):

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
                
        # transform action schemas into SAT
        for a in self.h_actions:
            new_sat_action = sat_action(a, str(self.dict[a.name]))
            self.sat_actions.append(new_sat_action)
    
    
    def build_sat_sentence(self, horizon, last_sentence=None, last_action=None):
        # use Hebrand names and convert to DIMACS later

        if last_sentence !=None:
            self.sat_sentence.append(last_sentence)
        
        # first clause is initial state
        clause = self.init_state.copy()
        for index,literal in enumerate(clause):
            clause[index]=literal+"0"
        self.sat_sentence.append(clause)
        
        # next comes the action schemas
        clause = []
        for action in self.h_actions:
            for precond in action.precond:
                clause.append("-" + action.name + str(horizon-1))
                clause.append(precond + str(horizon-1))
                self.sat_sentence.append(clause)
                clause = []
            for effect in action.effect:
                clause.append("-" + action.name + str(horizon-1))
                clause.append(effect + str(horizon))
                self.sat_sentence.append(clause)
                clause = []
                
        # next comes the frame axioms
        clause = []
        pred=copy.deepcopy(self.predicates)
        for index,p in enumerate(pred):
            pred[index]="-"+p
        pred=pred+copy.deepcopy(self.predicates)
        
        print(pred)
        for a in self.h_actions:
            for p in pred:
                if (p[0]!="-" and p not in a.effect and "-"+p not in a.effect):
                    clause.append("-" + p + str(horizon-1))
                    clause.append("-" + a.name + str(horizon-1))
                    clause.append(p + str(horizon))
                    self.sat_sentence.append(clause)
                    clause=[]
                if (p[0]=="-" and p[1:] not in a.effect and p not in a.effect):
                    clause.append(p[1:] + str(horizon-1))
                    clause.append("-" + a.name + str(horizon-1))
                    clause.append(p + str(horizon))
                    self.sat_sentence.append(clause)
                    clause=[]
                    
                    
        # lastly comes the effects
        if horizon>1 and last_action==None:
            for e in last_action.effect:
                if e[1]=="-" and e in self.sat_setence:
                    self.sat_sentence.remove(e)
                elif e not in self.sat_sentence:
                    self.sat_sentence.append(e)
                    
                    
                    
                    
    
    def convert2dimacs(self):
        # contruct dictionary
        i = 1
        for clause in self.sat_sentence:
            for lit in clause:
                litt = lit[0:]
                if litt not in self.dimacs2hebrand_dict.keys():
                    self.dimacs2hebrand_dict[litt] = i
                    i += 1
        
        # contruct DIMACS sentence
        for clause in self.sat_sentence:
            for lit in clause:
                if lit[0] == '-':
                    self.dimacs_sentence += '-' + str(self.dimacs2hebrand_dict[lit]) + ' '
                else:
                    self.dimacs_sentence += str(self.dimacs2hebrand_dict[lit]) + ' '
            self.dimacs_sentence += '0\n'
            
            
                    

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
        for a in self.h_actions:
            print("\t " + "A " + a.name)
            for p in list((a.precond)):
                print("\t\t: " + p)
            for e in list((a.effect)):
                print("\t\t-> " + e)
        print("SAT formulation:")
        print("\t " + "I " + ' '.join(self.sat_init_state))
        print("\t " + "G " + ' '.join(self.sat_goal_state))
        # falta imprimir aqui as acoes
        print("SAT dictionary:")
        # invert mapping for printing
#        inv_dict = dict((v,k) for k,v in self.dict.items())
#        for key in sorted(inv_dict.keys()):
#            print("\t" + str(key) + " : " + str(inv_dict[key]))
        inv_dict = dict((v,k) for k,v in self.dimacs2hebrand_dict.items())
        for key in sorted(inv_dict.keys()):
            print("\t" + str(key) + " : " + str(inv_dict[key]))

        
    def print_sentence(self):
        f = open("sat_sentence.txt", "w")
        for clause in self.sat_sentence:
            print(' '.join(clause), file=f)
        f.close()
        f = open("dimacs_sentence.txt", "w")
        print(self.dimacs_sentence, file=f)
        f.close()


class action:
    def __init__(self, name, precond, effect):
        self.nb_args = name.count(',')+1
        self.name    = name
        self.precond = precond
        self.effect  = effect


class sat_action:
    def __init__(self, act, sat):
        self.name     = act.name
        self.precond  = act.precond
        self.effect   = act.effect
        self.sat_code = sat




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
    pddl.hebrand2sat()
    pddl.build_sat_sentence(1)
    pddl.convert2dimacs()
    pddl.show()
    pddl.print_sentence()

if __name__ == "__main__":
	main()
