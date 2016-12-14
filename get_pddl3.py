import sys
import itertools
import copy
from dpll import *
from operator import itemgetter

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
        self.sat_sentence   = []
        self.dimacs_sentence = []
        

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

        for a in self.actions:
            for pred in a.precond + a.effect:
                if pred[0]!="-":
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
                combinations=list(itertools.product(self.consts,repeat=pred_info[1]))
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
            
     
        for predicate in self.predicates:
            if predicate in self.init_state:
                self.h_init_state.append(predicate)
            else:
                if predicate[0]!="-":
                    self.h_init_state.append("-"+predicate)
                else:
                    self.h_init_state.append(predicate[1:])


                    
        # transform action schemas into hebrand base
        for act in self.actions:
            action_name = act.name.split("(")
            action_args = get_letters(action_name[1]) #variables
            action_name = action_name[0]
            combinations = list(itertools.product(self.consts,repeat=act.nb_args))
            
            
            for listing in combinations:
                h_action_name = action_name + "(" + ','.join(listing) + ")"
                # convert preconditions into hebrand base
                h_precond = []
                for precond in act.precond:
                    dummy_precond = precond.split("(")
                    precond_name = dummy_precond[0]
                    precond_args = dummy_precond[1][0:len(dummy_precond[1])-1].split(",")
                    args = get_letters(dummy_precond[1])
                    for ii,i in enumerate(precond_args):
                        for ij,j in enumerate(action_args):
                            if i==j:
                                precond_args[ii]=listing[ij]
                    h_precond.append(precond_name+"("+','.join(precond_args)+")")
                    
                # convert effects in to hebrand base
                h_effects = []
                for effect in act.effect:
                    dummy_effect = effect.split("(")
                    effect_name = dummy_effect[0]
                    effect_args =dummy_effect[1][0:len(dummy_effect[1])-1].split(",")

                    for ii,i in enumerate(effect_args):
                        for ij,j in enumerate(action_args):
                            if i==j:
                                effect_args[ii]=listing[ij]
                    
                    h_effects.append(effect_name+"("+','.join(effect_args)+")")
                    self.h_actions.append(action(h_action_name, h_precond, h_effects))
        
                    
            
    
    def build_sat_sentence(self, horizon, last_sentence=None):
        # use Hebrand names and convert to DIMACS later
        
        # first clause is initial state
        if horizon==1:
            for literal in self.h_init_state:
                self.sat_sentence.append([literal+"0"])

        # next comes the action schemas
        
        for action in self.h_actions:
            for precond in action.precond:
                clause=[]
                clause.append("-"+action.name+str(horizon-1))
                clause.append(precond+str(horizon-1))
                self.sat_sentence.append(clause)

            for effect in action.effect:
                clause=[]
                clause.append("-"+action.name+str(horizon-1))
                clause.append(effect+str(horizon))
                self.sat_sentence.append(clause)
            #self.sat_sentence.append([])
        # next comes the frame axioms
        clause = []
        pred=copy.deepcopy(self.predicates)
        
        for a in self.h_actions:
            for p in pred:
                
                if (p not in a.effect and "-"+p not in a.effect):
                    clause.append("-" + p + str(horizon-1))
                    clause.append("-" + a.name + str(horizon-1))
                    clause.append(p + str(horizon))
                    self.sat_sentence.append(clause)
                    clause=[]

                    clause.append(p + str(horizon-1))
                    clause.append("-" + a.name + str(horizon-1))
                    clause.append("-" + p + str(horizon))
                    self.sat_sentence.append(clause)
                    clause=[]
                    
        #choose one action per frame
        action_list=[]
        for action in self.h_actions:
            action_list.append(action.name+str(horizon-1))
        self.sat_sentence.append(action_list)

        for index,i in enumerate(action_list):
            for j in action_list[index+1:]:
                self.sat_sentence.append(["-"+i,"-"+j])
             
        

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
        print("\t " + "I " + ' '.join(self.h_init_state))
        print("\t " + "G " + ' '.join(self.h_goal_state))
        # falta imprimir aqui as acoes
        print("SAT dictionary:")
        # invert mapping for printing
        inv_dict = dict((v,k) for k,v in self.dict.items())
        for key in sorted(inv_dict.keys()):
            print("\t" + str(key) + " : " + str(inv_dict[key]))
        
    def print_sentence(self,mode):
        f = open("sentence.txt", "w")
        if mode!=0:
            print("c "+sys.argv[1],file=f)
            print("p cnf"+str(len(self.dict))+" "+str(len(self.dimacs_sentence)),file=f)
            sentence=self.dimacs_sentence
        else:
            sentence=self.sat_sentence

        for clause in sentence:
            if mode==0:
                print(clause,file=f)
            else:
                for literal in clause:
                    print(literal,end=" ", file=f)
                print("0",file=f)
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










def add_goal_to_sentence(sentence,horizon,goal):
        #add goal state
        s=copy.deepcopy(sentence)
        for predicate in goal:
            s.append([predicate+str(horizon)])
        return s

def open_file(file):
    """reads input file"""

    pddl = PDDL()

    f = open(file)
    lines = f.readlines()
    
    for line in lines:
        words = list(line.split())
        if words!=[]:
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

def convert2dimacs(sentence,pddl):
    dictionary={}
    actions={}
    dimacs=copy.deepcopy(sentence)
    n=1
    for i,clause in enumerate(sentence):
        for j, literal in enumerate(clause):
            if literal not in dictionary:
                if literal[0]!="-":
                    dictionary[literal]=n
                    dictionary["-"+literal]=-n
                    dimacs[i][j]=dictionary[literal]
                    n=n+1
                else:
                    dictionary[literal]=-n
                    dictionary[literal[1:]]=n
                    for a in pddl.h_actions:
                        if literal[1:len(literal)-1] in a.name:
                            actions[literal[1:len(literal)]]=n
                    dimacs[i][j]=dictionary[literal]
                    n=n+1
                
            else:
                dimacs[i][j]=dictionary[literal]
                
    returning=[dictionary,dimacs,dict((k,v) for k,v in actions.items())]
    return returning
                




def main():
	
    pddl = open_file(sys.argv[1])
    pddl.hebrand_base()
    for h in range(1,2):
        print(h)
        pddl.build_sat_sentence(h)
        t_sentence=add_goal_to_sentence(pddl.sat_sentence,h,pddl.goal_state)
        D=convert2dimacs(t_sentence,pddl)
        pddl.dict=D[0]
        n_literals=int(len(pddl.dict)/2)        
        setup=[copy.deepcopy(D[1]),copy.deepcopy(D[1]),[0]*n_literals,[],[],0,[]]
        init_state=state(setup)
        result=dpll(init_state)
        if result[0]==False:
            continue
        else:
            break
    pddl.sat_sentence=t_sentence
    pddl.dimacs_sentence=D[1]
    action_ref=D[2]
    pddl.show()

    plan=[]
    if result[0]!=False:
        for key in action_ref.keys():
            if action_ref[key] in result[1]:
                plan.append([key,action_ref[key]])
        plan.sort(key = lambda row: row[1])

        print("")
        for step in plan:
            print(step[0])
        print("")
    pddl.print_sentence(0)
    print(h)
    inv_dict = dict((v,k) for k,v in pddl.dict.items())
    for i in range(0,h+1):
        for r in result[1]:
            if r!=0:
                if inv_dict[r][len(inv_dict[r])-1]==str(i) :#and inv_dict[r][0]!="-":
                    print(inv_dict[r])
        print("")
    print(result)

if __name__ == "__main__":
	main()
