import sys
import copy


class state:
    def __init__(self,setup):
        self.original   =setup[0]
        self.sentence   =setup[1]
        self.l_values   =setup[2]
        self.parent     =setup[3]
        self.children   =setup[4]
        self.depth      =setup[5]
        self.last_op    =setup[6]
        
    def show(self):
        print("---------------------------")
        print("Original sentence: ",end="")
        print(self.original)
        print("Sentence current Status: ",end="")
        print(self.sentence)
        print("Literal's values: ",end="")
        print(self.l_values)
        print("Literals of previous state: ",end="")
        print(self.parent)
        print("Literals of next states: ",end="")  
        print(self.children)
        print("Depth level: ",end="")
        print(self.depth)
        print("Last operation: ",end="")
        print(self.last_op)
        
        print("---------------------------")

    
    
    def assign(self,l_values):
        

        self.l_values=l_values
        assignment=copy.deepcopy(self.sentence)
        n_clauses=[]
        for i,clause in enumerate(self.sentence):
            for j in range(0,len(clause)):
                if self.sentence[i][j] in l_values:
                    assignment[i][j]=1
                else:
                    if -assignment[i][j] in l_values:
                        assignment[i][j]=-1
                    else:
                        assignment[i][j]=0
            if 1 in assignment[i]:
                n_clauses.append(1)
            else:
                if sum(assignment[i])==-len(assignment[i]):
                    n_clauses.append(-1)
                else:
                    n_clauses.append(0)
                    
        if sum(n_clauses)==len(n_clauses):
            self.sentence=True
        else:
            for i in reversed(range(0,len(n_clauses))):
                if n_clauses[i]==1:
                    assignment.pop(i)
                    self.sentence.pop(i)
                if n_clauses[i]==-1:
                    self.sentence=[]
                    break
                if n_clauses[i]==0:
                    for j,literal in reversed(list(enumerate(assignment[i]))):
                        if literal==-1:
                        
                            assignment[i].pop(j)
                            self.sentence[i].pop(j)
            
        
            

    def unit(self):
        unit=[]
        for clause in self.sentence:
            if len(clause)==1:
                unit.append(True)
            else:
                unit.append(False)
        return unit
    
    def pure(self):
        pure=[]; #Ex:[-2,1,5] - notx2,x1,x5 are pure
        n_pure=[]
        
        for clauses in self.sentence:
            for literal in clauses:
                """flag=0
                if pure==[]:
                    pure.append(literal)
                for index,p in enumerate(pure):
                    if p==-literal:
                        pure.pop(index)
                        n_pure.append(abs(p))
                        flag=1
                    if p==literal:
                        flag=1;
                if flag==0:
                    pure.append(literal)"""
                
                if literal not in n_pure and -literal not in n_pure:
                    if -literal in pure:
                        pure.remove(-literal)
                        n_pure.append(literal)
                    else:
                        if literal not in pure:
                            pure.append(literal)
                
                    
                    
        return pure





            

def children (current_state,assign):
    new_state=copy.deepcopy(current_state)
    new_state.l_values=assign
    new_state.assign(assign)
    new_state.parent=current_state.l_values
    new_state.children=[]
    new_state.depth=new_state.depth+1
    return new_state




def dpll (current_state):
    
    #SATISFABLE?
    if current_state.sentence==True:
        return [True,current_state.l_values]
   
    
    #EMPTY CLAUSE
    if current_state.sentence==[]:
        return [False,current_state.l_values]

    #UNIT
    unit=current_state.unit()
    for index,clause in enumerate(unit):
        if clause:
            l=current_state.sentence[index][0]
            assign=copy.deepcopy(current_state.l_values)
            assign[abs(l)-1]=l
                        
            new_state=children(current_state,assign)
            current_state.children.append(new_state.l_values)
            new_state.last_op=[l,"UNIT"]
            status=dpll(new_state)
            if status[0]==False:
                return status
            else:
                return status
    

    #PURE
    pure=current_state.pure()

    for l in pure:
        assign=copy.deepcopy(current_state.l_values)
        assign[abs(l)-1]=l

        new_state=children(current_state,assign)
        current_state.children.append(new_state.l_values)
        new_state.last_op=[l,"PURE"]
        status=dpll(new_state)
        if status[0]==False:
            return status
        else:
            return status


    #CHOOSE LITERAL
    for index,l in enumerate(current_state.l_values):
        if l==0:
            assign=copy.deepcopy(current_state.l_values)
            assign[index]=index+1
            new_state=children(current_state,assign)
            current_state.children.append(new_state.l_values)
            new_state.last_op=[assign[index],"CHOSEN"]
            status=dpll(new_state)
            if status[0]!=False:
                return status
            assign=[]
            assign=copy.deepcopy(current_state.l_values)
            assign[index]=-(index+1) 
            new_state=children(current_state,assign)
            current_state.children.append(new_state.l_values)
            new_state.last_op=[assign[index],"CHOSEN"]
            status=dpll(new_state)
            if status[0]==False:
                return status
            else:
                return status
    

    
            
def main ():
    #Exemplo
    n_literals=6
    sentence=[[-2,1],[1,2,-3],[-3],[-4,-1],[5],[6,1],[-1,-2,-3]]
    #sentence=[[1,-2],[2,-3],[3,-4],[4,-5],[5,-6],[6]]
    setup=[copy.deepcopy(sentence),copy.deepcopy(sentence),[0]*n_literals,[],[],0,[]]
    init_state=state(setup)
    
    dpll(init_state)
    
if __name__ == "__main__":
	main()
