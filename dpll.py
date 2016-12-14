import sys
import copy


class state:
    def __init__(self,setup):
        self.original   =setup[0]   # original sentence
        self.sentence   =setup[1]   # sentence after assignments to literals
        self.l_values   =setup[2]   # values assigned to literals
        self.parent     =setup[3]   # values assigned to literals from the previous state
        self.children   =setup[4]   # values assigned to literals from next states
        self.depth      =setup[5]   # depth of the state
        self.last_op    =setup[6]   # operation that lead to this state
        

    
    #assigns values to literals and rebuilds the sentence
    def assign(self,l_values):
        
        #registers the values
        self.l_values=l_values
        assignment=copy.deepcopy(self.sentence)

        #to check if sentence is true (list of 1s)
        n_clauses=[]
        for i,clause in enumerate(self.sentence):
            for j in range(0,len(clause)):
                #if literal is already assigned and its equal
                if self.sentence[i][j] in l_values:
                    #Then its true (1)
                    assignment[i][j]=1
                else:
                    #if literal is already assigned and its not equal
                    if -assignment[i][j] in l_values:
                        #Then its false
                        assignment[i][j]=-1
                    else:
                        #cannot say anything about it yet
                        assignment[i][j]=0
            #if a literal is true in a clause, then the clause is true        
            if 1 in assignment[i]:
                n_clauses.append(1)
            else:
                #if all literals are false, the sentence is false
                if sum(assignment[i])==-len(assignment[i]):
                    n_clauses.append(-1)
                else:
                    n_clauses.append(0)
        
        #if all clauses are true, the sentence is true
        if sum(n_clauses)==len(n_clauses):
            self.sentence=True
        else:
            #Lets filter the sentence from already know info
            for i in reversed(range(0,len(n_clauses))):
                #if a clause is true, remove it
                if n_clauses[i]==1:
                    assignment.pop(i)
                    self.sentence.pop(i)
                #if a clause is false, the sentence is false, returns []
                if n_clauses[i]==-1:
                    self.sentence=[]
                    break
        
                if n_clauses[i]==0:
                    #for every literal in clause
                    for j,literal in reversed(list(enumerate(assignment[i]))):
                        #if literal is false, remove it from clause
                        if literal==-1:
                        
                            assignment[i].pop(j)
                            self.sentence[i].pop(j)
            
        
            
    #checks which clauses are unit clauses (T/F)
    def unit(self):
        unit=[]
        for clause in self.sentence:
            if len(clause)==1:
                unit.append(True)
            else:
                unit.append(False)
        return unit
    
    #returns assignments of pure literals
    def pure(self):
        pure=[]
        n_pure=[]
        
        for clauses in self.sentence:
            for literal in clauses:
                #if literal and its opposite are not in not pure list
                if literal not in n_pure and -literal not in n_pure:
                    #if pure already has its opposite, that literal is removed from pure list and added to the no pure list
                    if -literal in pure:
                        pure.remove(-literal)
                        n_pure.append(literal)
                    else:
                        #If literal is pure and not in pure list, add it
                        if literal not in pure:
                            pure.append(literal)
                
                    
                    
        return pure





            
#creates children state of current_state
def children (current_state,assign):
    new_state=copy.deepcopy(current_state)
    new_state.l_values=assign

    #this will update the sentence of new_state
    new_state.assign(assign)

    new_state.parent=current_state.l_values
    new_state.children=[]
    new_state.depth=new_state.depth+1
    return new_state



#DPLL SAT solver
def dpll (current_state):
    
    #SATISFABLE?
    if current_state.sentence==True:
        return [True,current_state.l_values]
   
    
    #EMPTY CLAUSE
    if current_state.sentence==[]:
        return [False,current_state.l_values]

    #UNIT
    unit=current_state.unit()
    #for every clause
    for index,clause in enumerate(unit):
        #if unit
        if clause:
            #new value to be assigned
            l=current_state.sentence[index][0]
            assign=copy.deepcopy(current_state.l_values)
            #Ex of assign:[1,-2,3]
            assign[abs(l)-1]=l
                        
            new_state=children(current_state,assign)
            current_state.children.append(new_state.l_values)
            new_state.last_op=[l,"UNIT"]
            #reruns DPLL with new assignment
            status=dpll(new_state)
            return status
    

    #PURE
    pure=current_state.pure()
    #for every pure value
    for l in pure:
        assign=copy.deepcopy(current_state.l_values)
        assign[abs(l)-1]=l

        new_state=children(current_state,assign)
        current_state.children.append(new_state.l_values)
        new_state.last_op=[l,"PURE"]
        status=dpll(new_state)
        return status


    #CHOOSE LITERAL
    for index,l in enumerate(current_state.l_values):
        #if literal is not assigned
        if l==0:
            #put True
            assign=copy.deepcopy(current_state.l_values)
            assign[index]=index+1
            new_state=children(current_state,assign)
            current_state.children.append(new_state.l_values)
            new_state.last_op=[assign[index],"CHOSEN"]
            status=dpll(new_state)
            #if it is not giving the right answer, it tries to put the literal to false
            if status[0]==True:
                return status

            #put False
            assign=[]
            assign=copy.deepcopy(current_state.l_values)
            assign[index]=-(index+1) 
            new_state=children(current_state,assign)
            current_state.children.append(new_state.l_values)
            new_state.last_op=[assign[index],"CHOSEN"]
            status=dpll(new_state)
            return status
