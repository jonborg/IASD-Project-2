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
        self.sat_sentence   = []    # sentence
        self.dimacs_sentence = []   # sentence in DIMACS
        

    def add_action(self, action):
        self.actions.append(action)
        
    #counts constantes
    def count_consts(self, predicate):
        predicate=predicate[0:len(predicate)-1].split("(")

        #list of constantes in predicate
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

                    #info about the predicate (its name and number of arguments)
                    info=[pred_name, nb_args]

                    #if that info was already seen. If not, it is added to the list of predicates
                    if info in p_list:
                        continue
                    else:
                        p_list.append(info)
        
               
        for pred_info in p_list:
            #if the analised predicate has more than 1 argument
            if pred_info[1]>1:
                #combinations of not repeating constants 
                combinations=list(itertools.permutations(self.consts,pred_info[1]))
            else:
                combinations=self.consts

            #for every combination
            for listing in combinations:
                predicate=pred_info[0] + "("
                for i in range (pred_info[1]):
                
                    #if it is put the last variable
                    if i==pred_info[1]-1:
                        #adds final variable
                        predicate += listing[i] + ")"
                    else:
                        #adds a variable and a comma
                        predicate += listing[i] + ","
                #adds predicate to list of predicates 
                self.predicates.append(predicate)
            
        #hebrand of initial state
        for predicate in self.predicates:
            #if predicate in initial state
            if predicate in self.init_state:
                self.h_init_state.append(predicate)

            #if not, add/remove a minus sign if predicate does/doesn't have it
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
            combinations = list(itertools.permutations(self.consts,act.nb_args))
           
            
            for listing in combinations:
                h_action_name = action_name + "(" + ','.join(listing) + ")"
                # convert preconditions into hebrand base
                h_precond = []

                #to check if a precondition has a constant that was added as argument to the action
                flag=0
                for precond in act.precond:
                    dummy_precond = precond.split("(")
                    precond_name = dummy_precond[0]
                    precond_args = dummy_precond[1][0:len(dummy_precond[1])-1].split(",")
                    #checks every precondition arguments
                    for p in precond_args:
                        if p in listing:
                            #it means that this hebranded action is not used ex:move2table(Table,A)
                            flag=1
                            break
                    if flag==1:
                        break
                    
                    for ii,i in enumerate(precond_args):
                        for ij,j in enumerate(action_args):
                            #if argument in precondition has same letter as the argument of action
                            if i==j:
                                #sets constant
                                precond_args[ii]=listing[ij]
                    h_precond.append(precond_name+"("+','.join(precond_args)+")")
                if flag==1:
                    continue
                flag=0
                # convert effects in to hebrand base
                h_effects = []
                for effect in act.effect:
                    dummy_effect = effect.split("(")
                    effect_name = dummy_effect[0]
                    effect_args =dummy_effect[1][0:len(dummy_effect[1])-1].split(",")

                    #checks every effect arguments
                    for e in effect_args:
                        if e in listing:
                            flag=1
                            break
                    if flag==1:
                        break
                    for ii,i in enumerate(effect_args):
                        for ij,j in enumerate(action_args):
                            #if argument in effect has same letter as the argument of action
                            if i==j:
                                effect_args[ii]=listing[ij]
                        
                    
                    h_effects.append(effect_name+"("+','.join(effect_args)+")")
                if flag==1:
                    continue
                else:
                    #adds hebranded action to list of hebranded actions
                    self.h_actions.append(action(h_action_name, h_precond, h_effects))
                
                    
            
    
    def build_sat_sentence(self, horizon, last_sentence=None):
        # use Hebrand names and convert to DIMACS later
        
        # first clause is initial state
        if horizon==1:
            for literal in self.h_init_state:
                self.sat_sentence.append([literal+"0"])

        # next comes the action schemas
        #action => precond ^ effects = (-action V precond) ^ (-action V effects)
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
        # next comes the frame axioms
        clause = []
        pred=copy.deepcopy(self.predicates)
        
        #(untouched0 ^ action0 => untouched1) ^ (-untouched0 ^ action0 => -untouched1)=
        #=(-untouched V - action0 V untouched1) ^(untouched0 V -action0 V -untouched1)
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
        #Must choose at least 1 action
        for action in self.h_actions:
            action_list.append(action.name+str(horizon-1))
        self.sat_sentence.append(action_list)
        #must one action at least
        for index,i in enumerate(action_list):
            for j in action_list[index+1:]:
                self.sat_sentence.append(["-"+i,"-"+j])
             
        







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









#adds goal sentence to sentence
def add_goal_to_sentence(sentence,horizon,goal):
        s=copy.deepcopy(sentence)
        for predicate in goal:
            s.append([predicate+str(horizon)])
        return s
    
#reads input file
def open_file(file):

    pddl = PDDL()

    f = open(file)
    lines = f.readlines()
    
    for line in lines:
        words = list(line.split())
        if words!=[]:
            #Initial state line
            if words[0] == 'I':
                pddl.init_state = words[1:]
            #Goal state line
            if words[0] == 'G':
                pddl.goal_state = words[1:]
            #Actions lines
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

                #add action to list of actions available
                new_action = action(name, preconditions, effects)
                pddl.add_action(new_action)

    f.close()
    return pddl

#coberts sentence to DIMACS syntax
def convert2dimacs(sentence,pddl):
    #DIMACS table
    dictionary={}
    #aDIMACS ctions table
    actions={}
    dimacs=copy.deepcopy(sentence)
    n=1
    for i,clause in enumerate(sentence):
        for j, literal in enumerate(clause):
            #if analised literal not in the dictionary yet
            if literal not in dictionary:
                #if literal "positive"
                if literal[0]!="-":
                    #add it and its opposite
                    dictionary[literal]=n
                    dictionary["-"+literal]=-n
                    #changes literal to its DIMACS value
                    dimacs[i][j]=dictionary[literal]
                    n=n+1
                else:
                    #add it and its opposite
                    dictionary[literal]=-n
                    dictionary[literal[1:]]=n
                    #if literal is an action add it to DIMACS action table
                    for a in pddl.h_actions:
                        if literal[1:len(literal)-1] in a.name:
                            actions[literal[1:len(literal)]]=n
                    #changes literal to its DIMACS value
                    dimacs[i][j]=dictionary[literal]
                    n=n+1
                
            else:
                dimacs[i][j]=dictionary[literal]
                
    returning=[dictionary,dimacs,dict((k,v) for k,v in actions.items())]
    return returning
                

