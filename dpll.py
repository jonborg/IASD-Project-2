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
        ic=0
        while ic<len(self.sentence):
            f=1 #A flag. if clause is true f=0, otherwise it will stay 1
            il=0
            while il<len(self.sentence[ic]):
                for l in l_values:
                
                    if f==1:
                        if self.sentence[ic][il]==l:
                            f=0; #a clausula não é falsa
                            break
                        if self.sentence[ic][il]==-l:
                            if len(self.sentence[ic])==1:
                                self.sentence=[]
                                return
                            self.sentence[ic].pop(il)
                            il=il-1
                            break
                il=il+1
          
            if f==0:
                self.sentence.pop(ic)
                ic=ic-1
            ic=ic+1
        if self.sentence==[]:
            self.sentence=True

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
                flag=0
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
    current_state.show()

    #SATISFABLE?
    if current_state.sentence==True:
        return True
    
    #EMPTY CLAUSE
    if current_state.sentence==[]:
        return False

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
            return dpll(new_state)

    #PURE
    pure=current_state.pure()
    for l in pure:
        assign=copy.deepcopy(current_state.l_values)
        assign[abs(l)-1]=l

        new_state=children(current_state,assign)
        current_state.children.append(new_state.l_values)
        new_state.last_op=[l,"PURE"]
        return dpll(new_state)

    #CHOOSE LITERAL
    for index,l in enumerate(current_state.l_values):
        if l==0:
            assign=copy.deepcopy(current_state.l_values)
            assign[index]=index+1
            new_state=children(current_state,assign)
            current_state.children.append(new_state.l_values)
            new_state.last_op=[l,"CHOSEN"]
            return dpll(new_state)

            assign=copy.deepcopy(current_state.l_values)
            assign[index]=-(index+1) 
            new_state=children(current_state,assign)
            current_state.children.append(new_state.l_values)
            new_state.last_op=[l,"CHOSEN"]
            return dpll(new_state)



        
            
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
