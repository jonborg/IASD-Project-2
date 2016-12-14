import sys
from cnf_converter import *
from dpll import *

def main():
    #read input file
    pddl = open_file(sys.argv[1])

    #Makes the hebrand expansion of initial state and actions
    pddl.hebrand_base()

    #horizon
    h=0
    while 1:
        h=h+1

        #builds the sentence, beliving that the goal is reached in h steps
        pddl.build_sat_sentence(h)
        t_sentence=add_goal_to_sentence(pddl.sat_sentence,h,pddl.goal_state)

        #returns DIMACS convertion table, the sentence translated to DIMACS and the DIMACS action table
        D=convert2dimacs(t_sentence,pddl)
        pddl.dict=D[0]
        n_literals=int(len(pddl.dict)/2)

        #Initial setup for SAT solver
        setup=[copy.deepcopy(D[1]),copy.deepcopy(D[1]),[0]*n_literals,[],[],0,[]]
        init_state=state(setup)

        #returns true or false and the solution arrived by DPLL
        result=dpll(init_state)

        #if false goes to next iteration. If true, it stops the cycle
        if result[0]==False:
            continue
        else:
            break
    
    pddl.sat_sentence=t_sentence
    pddl.dimacs_sentence=D[1]
    action_ref=D[2]

    plan=[]
    
    #checks if the actions in the action table are positive in the results
    for key in action_ref.keys():
        if action_ref[key] in result[1]:
            plan.append([key,action_ref[key]])
    plan.sort(key = lambda row: row[1])

    #prints the plan to the display
    for step in plan:
        ss = step[0].split('(')
        aa=ss[1][0:len(ss[1])-2].split(",")
        print(ss[0] + ' ' + ' '.join(aa))

if __name__ == "__main__":
	main()
