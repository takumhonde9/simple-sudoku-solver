#!/usr/bin/python3

import sys, getopt

class SatInstance:
    def __init__(self):
        pass
    def from_file(self, inputfile):
        self.clauses = list()
        self.VARS = set()
        self.p = 0
        self.cnf = 0
        with open(inputfile, "r") as input_file:
            self.clauses.append(list())
            maxvar = 0
            for line in input_file:
                tokens = line.split()
                if len(tokens) != 0 and tokens[0] not in ("p", "c"):
                    for tok in tokens:
                        lit = int(tok)
                        maxvar = max(maxvar, abs(lit))
                        if lit == 0:
                            self.clauses.append(list())
                        else:
                            self.clauses[-1].append(lit)
                if tokens[0] == "p":
                    self.p = int(tokens[2])
                    self.cnf = int(tokens[3])
            assert len(self.clauses[-1]) == 0
            self.clauses.pop()
            if not (maxvar == self.p):
                print("Non-standard CNF encoding!")
                sys.exit(5)
      # Variables are numbered from 1 to p
        for i in range(1,self.p+1):
            self.VARS.add(i)
    def __str__(self):
        s = ""
        for clause in self.clauses:
            s += str(clause)
            s += "\n"
        return s



def main(argv):
   inputfile = ''
   verbosity=False
   inputflag=False
   try:
      opts, args = getopt.getopt(argv,"hi:v",["ifile="])
   except getopt.GetoptError:
      print ('DPLLsat.py -i <inputCNFfile> [-v] ')
      sys.exit(2)
   for opt, arg in opts:
       if opt == '-h':
           print ('DPLLsat.py -i <inputCNFfile> [-v]')
           sys.exit()
    ##-v sets the verbosity of informational output
    ## (set to true for output veriable assignments, defaults to false)
       elif opt == '-v':
           verbosity = True
       elif opt in ("-i", "--ifile"):
           inputfile = arg
           inputflag = True
   if inputflag:
       instance = SatInstance()
       instance.from_file(inputfile)
       solve_dpll(instance, verbosity)
   else:
       print("You must have an input file!")
       print ('DPLLsat.py -i <inputCNFfile> [-v]')

## support functions for DLL -- might make them a class ##
## maybe create a cache for the unit clauses
def flatten(mda):
    """
    This function takes a 2 dimensional arr and returns a 1 dimensional array
    note: mda - multidimensional array
    """
    from functools import reduce
    if len(mda) == 0:
        return []
    return reduce(lambda x,y :x+y ,mda)

def filter(f):
    unitClauseSet=generate_unit_clauses(f)
    fFiltered=[]
    for clause in f:
        for literal in clause:
            if not literal in unitClauseSet:
                fFiltered.append(clause)
                break
    return fFiltered

def most_frequent_in(l):
    """
    This function finds the literal that appears the most in the flattened
    version of f, noted as l.
    """
    mydict   = {}
    cnt, itm = 0, ''
    for item in reversed(l):
         mydict[item] = mydict.get(item, 0) + 1
         if mydict[item] >= cnt :
             cnt, itm = mydict[item], item

    return itm

def most_frequent_heuristic(vars, f):
    from operator import itemgetter
    """
    This function implements a heuristic that finds the most frequently
    appearing literal
    """
    fFiltered = filter(f)
    fFlattened=flatten(fFiltered)
    for elem in fFlattened:
        if elem<0:
            elem=-elem
    return most_frequent_in(fFlattened)

def maxo(lit, f):
    """
    This function finds the number of occurences of a literal, lit in f
    """
    count=0
    for literal in f:
        if lit==literal:
            count+=1
    return count

def moms(lit, f):
    """
    This function finds the number of occurences of a literal, lit in the min
    sized clauses containing lit.
    """
    minSizedClause=[]
    minSize=0
    for clause in f:
        if lit in clause:
            if len(clause) < minSize:
                minSize=len(clause)
    countofl=0
    for clause in f:
        if lit in clause and len(clause)==minSize:
            countofl+=clause.count(lit)

    return  countofl

def mams_heuristic(vars, f):
    """
    Citation:
    """
    fFiltered=flatten(filter(f))
    v=0
    lit_max=""
    for literal in fFiltered:
        if v < maxo(literal, fFiltered)+moms(literal, f):
            lit_max=literal
    return lit_max

def pick_variable(vars, f): # needs alteration: avoid picking var in unit clause
    """
    This function is an auxiliary function that is used to pick a variable that
    should be explored next by the dpll algorithm
    Heuristic: Most frequent variable
    """
    # trying to avoid picking a variable that is contained in a unit clause
    #return most_frequent_heuristic(vars, f)
    return mams_heuristic(vars,f)


def isEmptyClause(vars, f):
    """
    This function returns true if all the clauses in the list f are empty.
    E.g. [[],[],[],...,[]] or set(flatten([[x1][x2][x3],..[xn]])) != VARS
    """
    for clause in f:
        if len(clause) > 1:
            return False
    fVars=generate_vars_in(f)
    if (fVars != vars) or (foundContradiction(vars, f)):
        return True
    # might never reach this
    if len(f) == 0:
        return True

def generate_vars_in(f):
    """
    This function generates all the variables contained in f
    """
    fVars=set()
    for literal in set(flatten(f)):
        if literal<0:
            fVars.add(-literal)
            continue
        fVars.add(literal)
    return fVars

def foundContradiction(vars, f):
    """
    This function checks whether this unit clause set contains any positive
    literal with a negated pair
    """

    unitClauseSet=generate_unit_clauses(f)
    for literal in unitClauseSet:
        if -literal in unitClauseSet:
            return True
    return False

def isConsistent(vars, f): # missing func definition
    from math import pow, ceil
    """
    This is an auxiliary function that checks whehter or not a CNF is consistent.
    A CNF is consistent if ...
    """
    if foundContradiction(vars, f):
        return False

    for clause in f:
        if len(clause) >1:
            return False
    fVars = generate_vars_in(f)

    count=0
    for literal in set(flatten(f)):
        if literal>0:
            count+=1

    if count < ceil(pow(len(vars), (1/3)))**2:
        return False

    if fVars == vars:
        return True
    return False

def generate_unit_clauses(f):
    """
    This function generates all the unit clauses in f
    """
    unitClauseSet = set()
    for clause in f:
        if len(clause) == 1:
            unitClauseSet.add(clause[0])
    return unitClauseSet

def propagate_units(f):
    """
    This function removes all clauses with unit clause literals and removes negated
    literals of unit clauses within clauses of CNF.
    """
    toBeRemoved = []; toBeAdded = []
    unitClauseSet=generate_unit_clauses(f)
    for clause in f:
        for literal in clause:
            if literal in unitClauseSet and len(clause)> 1:
                toBeRemoved.append(clause)
                break
            if -literal in unitClauseSet :
                tempClause=clause
                toBeRemoved.append(clause)
                tempClause.remove(literal) # remove unit clause with sign flipped
                toBeAdded.append(tempClause)

    for clause in toBeAdded:
        f.append(clause)
    for clause in toBeRemoved:
        if clause in f:
            f.remove(clause)
    return f

def generate_pure_elems(f):
    """
    This function returns the set of pure literals in f
    """
    fFlattened = set(flatten(f)) # flatten list & make set
    # generate all elems that are not pure
    pureLiterals = []
    unitClauseSet = set()
    for literal in fFlattened:
        if not -literal in fFlattened:
            pureLiterals.append(literal)
    return set(pureLiterals)

def pure_elim(f, vars):
    """
    This function removes all clauses with pure elements.
    """
    toBeRemoved=[]
    toBeAdded=[]
    pureElems = generate_pure_elems(f)
    for clause in f:
        for literal in clause:
            if literal in pureElems:
                toBeRemoved.append(clause)
                toBeAdded.append(literal)

    for e in toBeAdded:
        f.append([e])
    for e in toBeRemoved:
        if e in f:
            f.remove(e)

def solve(vars, f):
    from copy import deepcopy
    """
    This function performs dpll recursively, some additions made:
        - repeatedly perform propagate_units until you can no longer do so
        - if pick a var that results in a contradiction (with unit clause)
          return empty clause
        -
    """
    second=set()
    while True :
        first=generate_unit_clauses(propagate_units(f))
        if first==second:
            break
        second=generate_unit_clauses(propagate_units(f))

    pure_elim(f,vars)

    if isEmptyClause(vars, f):
        return []
    if isConsistent(vars, f):
        return f
    x=pick_variable(vars, f)

    if foundContradiction(vars, f):
        return []

    sol=solve(vars, deepcopy(f)+[[x]])
    if not isEmptyClause(vars, sol):
        return sol
    else:
        sol=solve(vars, deepcopy(f)+[[-x]])
        return sol

def convert_to_sudoku_value(literal, N):
    """
    This function converts a litera to a sudoku val
    """
    if literal%N == 0:
        return N
    return literal%N

def pretty_print(sol, N):
    """
    This function pretty prints the solution to represent a solved sudoku
    puzzle based on given constraints. Note: we did not consider 3-by-3
    constraints
    """
    count=1
    vars=set(flatten(sol))
    for var in vars:
        if count>N:
            print(""); count=1
        if var > 0:
            print(convert_to_sudoku_value(var, N), end=" ")
        count+=1


def print_literals(sol):
    """
    This function prints the literals in the following way:
        line of positve literals
        line of negative literals
    """
    sol = set(flatten(sol))
    for literal in sol:
        if literal>0:
            print(literal, " ",end="")
    print("")
    for literal in sol:
        if literal<0:
            print(literal, " ",end="")
    print("")

""" Question 2 """
# Finds a satisfying assignment to a SAT instance,
# using the DPLL algorithm.
# Input: a SAT instance and verbosity flag
# Output: print "UNSAT" or
#    "SAT"
#    list of true literals (if verbosity == True)
#    list of false literals (if verbosity == True)
#
#  You will need to define your own
#  solve(VARS, F), pure-elim(F), propagate-units(F), and
#  any other auxiliary functions
def solve_dpll(instance, verbosity):
    from math import pow, ceil
    #print(instance) -- array of arrays containing conjuncts
    #print(instance.VARS) --  array of vars
    #print(verbosity)
    #################################################
    # Start your code
    f = instance.clauses
    vars = instance.VARS
    sol=solve(vars, f)
    if len(sol) == 0:
        print("UNSAT")
    else:
        print("SAT")
        if verbosity==True:
            print_literals(sol)
            pretty_print(sol, ceil(pow(len(vars), (1/3))))
    # End your code
    return True
    #################################################

if __name__ == "__main__":
   main(sys.argv[1:])
