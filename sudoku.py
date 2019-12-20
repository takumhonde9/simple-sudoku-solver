#!/usr/bin/python3

import sys, getopt
#####################################################
#####################################################
# Please enter the number of hours you spent on this
# assignment here
# num_hours_i_spent_on_this_assignment = 20
#####################################################
#####################################################

#####################################################
#####################################################
# Give one short piece of feedback about the course so far. What
# have you found most interesting? Is there a topic that you had trouble
# understanding? Are there any changes that could improve the value of the
# course to you? (We will anonymize these before reading them.)
# <Your feedback goes here>
"""
This was a fun assignment. Wish we had more time and a few more
resources to speed up working on it e.g. some papers to refer to
"""
#####################################################
#####################################################

### cant get input file do

def main(argv):
    inputfile = ''
    N=0
    try:
        opts, args = getopt.getopt(argv,"hn:i:",["N=","ifile="]) # this is being weird
    except getopt.GetoptError:
        print ('sudoku.py -n <size of Sodoku> -i <inputputfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print ('sudoku.py  -n <size of Sodoku> -i <inputputfile>')
            sys.exit()
        elif opt in ("-n", "--N"):
            N = int(arg)
        elif opt in ("-i", "--ifile"):
            inputfile = arg
    instance = readInstance(N, inputfile)
    toCNF(N,instance,inputfile+str(N)+".cnf")




def readInstance (N, inputfile):
    if inputfile == '':
        return [[0 for j in range(N)] for i in range(N)]
    with open(inputfile, "r") as input_file:
        instance =[]
        for line in input_file:
            number_strings = line.split() # Split the line on runs of whitespace
            numbers = [int(n) for n in number_strings] # Convert to integers
            if len(numbers) == N:
                instance.append(numbers) # Add the "row" to your list.
            else:
                print("Invalid Sudoku instance!")
                sys.exit(3)
        return instance # a 2d list: [[1, 3, 4], [5, 5, 6]]


""" Question 1 """
def toCNF (N, instance, outputfile):
    """ Constructs the CNF formula C in Dimacs format from a sudoku grid."""
    """ OUTPUT: Write Dimacs CNF to output_file """
    output_file = open(outputfile, "w")
    "*** YOUR CODE HERE ***"
    # for row in instance:
    #     print(row)
    # print("")
    c1="" # constraint 1's sentence
    c2="" # constraint 2's sentence
    c3="" # constraint 3's sentence
    c4="" # constraint 4's sentence
    c5="" # constraint 5's sentence
    counter=0
    numClauses = 0
    for i in range (0, N):
        for j in range (0, N):
            for k in range (1, N+1):
                var1 = N*(i*N+j)+k

                # constraint 1
                c1 += str(var1) + " "

                # constraint 2
                # example: ~(0,0,1) V ~(0,0,2) ^ ~(0,0,1) V ~(0,0,3) ...
                for l in range(k+1,N+1):
                    var2 = N*(i*N+j)+l
                    #print("(~(",i+1,", ",j+1,", ",k,") v ","~(",i+1,", ",j+1,", ",l,")) ^ ")
                    c2 += str(-var1) + " " + str(-(var2)) + " 0 "
                    numClauses+=1

                # constraint 3
                # example: ~(0,0,4) V ~(0,1,4) ^ ~(0,0,4) V ~(0,2,4) ...
                for l in range(j+1,N):
                    var2 = N*(i*N+l)+k
                    #print(var1, ", ", var2)
                    #print("(~(",i+1,", ",j+1,", ",k,") v ","~(",i+1,", ",l+1,", ",k,")) ^ ")
                    c3 += str(-var1) + " " + str(-(var2)) + " 0 "
                    numClauses+=1

                # constraint 4
                # example: ~(0,0,4) V ~(1,0,4) ^ ~(0,0,4) V ~(2,0,4) ...
                for l in range(i+1,N):
                    var2 = N*(l*N+j)+k
                    #print(var1, ", ", var2)
                    #print("(~(",i,", ",j,", ",k,") v ","~(",l,", ",j,", ",k,")) ^ ")
                    c4 += str(-var1) + " " + str(-(var2)) + " 0 "
                    numClauses+=1

                # constraint 5
                if instance[i][j] == k:
                    counter +=1
                    c5 += str(var1) + " 0 "
                    numClauses+=1

            c1 += "0 "
            numClauses+=1

    #final constraint
    c = "c sudoku-solving cnf file"+"\n"
    c += "c "+str(N)+"-by-"+str(N)+" grid with "+str(counter)+" filled entries."+"\n"
    c += "p cnf "+str(N*N*N)+" "+str(numClauses)+"\n"+c1+c2+c3+c4+c5
    #print(c) for debugging

    output_file.write(c)
    "*** YOUR CODE ENDS HERE ***"
    output_file.close()


if __name__ == "__main__":
   main(sys.argv[1:])
