#EE19B070
#EE2703
#Assignment 2 - Solving A Circuit 

#The cnvention I have followed is that Vac == Vp-p - voltage peak to peak
#therefore Vmax of ac is Vpp/2

#I also took the conventin that V node1 node2 V'
#is modeled by the equation Vnode1 - Vnode2 = V'


import sys
import numpy as np
import math
try:
    arg1=sys.argv[1]     #input the file to read, from command line
except Exception:
    print("Please enter a filename as command line arguement") #Error if no arguement is passed in command line
    exit()
try:
    with open(arg1) as f:     #opens the file
        lines=f.readlines()   #creates the list of lines with each line as strings
except IOError:
    print("Invalid Filename")  #Error if the input filename is not in directory
    exit()
CIRCUIT=".circuit"   #variables
END=".end"
AC_KEY=".ac"
start=-1
end=-2
ac=0    #ac stores 0 if there's no AC source
AC=0
n1=0
n2=0
for a in range(0,len(lines)):
    if lines[a][:len(CIRCUIT)]==CIRCUIT:
        start=a     #identifies start line of the block
        n1+=1
    elif lines[a][:len(END)]==END:
        end=a       #identifies end line of the block
        n2+=1
    elif lines[a][:len(AC_KEY)]==AC_KEY:
        if AC!=0:
            continue
        ac=lines[a].split()   #identifies ac source
        AC+=a
if AC<end:
    AC=0
if start>end or n1>1 or n2>1:
    print("Invalid Circuit definition.")   #Validates circuit block
    exit()
circuit_block=lines[start+1:end]     #circuit block

parsing=[]     #list of lists of information from netlist file
for i in range(0,len(circuit_block)):
    line=circuit_block[i].split("#")[0].split() #removes the comments in each line, if present
    if len(line)==0:   #this is for certain cases where an entire line is a comment
        continue
    l2=[]
    for j in range(0,len(line)):
        l2.append(line[j])
    parsing.append(l2)
#for DC
if AC==0:
    for i in parsing:
        if i[0]=='.ac':
            z=parsing.node2.index(i)
            del parsing[z]

#Creating a dictionary to store all the nodes
nodes = {}         #dictionary that stores the node names as values
V=['GND']      # X matrix : node voltages and currents through voltage sources
node2 = []
for i in range(0,len(parsing)):
    if parsing[i][1] in nodes.values():
        if parsing[i][2] in nodes.values():
            continue
        else:
            nodes[len(nodes)]=parsing[i][2]
            V.append('V'+nodes[len(nodes)-1])
            node2.append(nodes[len(nodes)-1])
    else:
        nodes[len(nodes)]=parsing[i][1]
        V.append('V'+nodes[len(nodes)-1])
        node2.append(nodes[len(nodes)-1])
nodekey=list(nodes.keys())     #list of all the keys of the dictionary nodes
nodeval=list(nodes.values())   #list of all the values of the dictionary nodes


#print(nodes)
#print(node2)


class CircElement():    #creating a class for each circuit element (not necessary but makes the syntax a little clearer)
    
    def __init__(self,info):  #defining all the parameters
        self.name = info[0]
        self.terminal1 = info[1]
        self.terminal2 = info[2]
        self.value = info[3]

k = (len(parsing));
element = ['']*k;     #initialising the nested list "element"
for n in range(k):
    element[n] = CircElement(parsing[n]);

NumVolSource = 0;       #calculating number of voltage sources
for n in range(k):
    h = element[n].name;
    if h[0] == "V":
        NumVolSource += 1

num_nodes = 0       #calculating number of nodes
for n in range(len(parsing)):

        if (node2.index(element[n].terminal1) >= num_nodes or node2.index(element[n].terminal2) >= num_nodes) and node2.index(element[n].terminal1) > node2.index(element[n].terminal2) :
            num_nodes = node2.index(element[n].terminal1)  
            #If its not present thena dd or else if it is present, just continue
        elif (node2.index(element[n].terminal1) >= num_nodes or node2.index(element[n].terminal2) >= num_nodes) and node2.index(element[n].terminal1) < node2.index(element[n].terminal2) :
            num_nodes = node2.index(element[n].terminal2)
        else:
            continue
print("\nThe total number of nodes present are : {} , (excluding GND) ".format(num_nodes))
node2.remove('GND')     #sorting all the alphanumeric elements
node2.sort()
node2.insert(0,'GND')
#print(node2)

Mat_length = int(num_nodes + NumVolSource)      #calculating the length of the matrix
B = np.zeros((int(Mat_length),1) ,dtype = complex)
A = np.zeros((int(Mat_length),int(Mat_length)) ,dtype = complex)

if AC!=0:
    w = math.pi*2*float(ac[-1])     #w = 2*pi*freq
#print(w)

for k2 in range(int(Mat_length)):       #start of filling in the LHS A matrix
    for k1 in range(int(Mat_length)):

        if k2 == k1 and k1 < num_nodes:     #filling in the diagonals, i.e when k1 == k2
            for n in range(len(parsing)):
                if (node2.index(element[n].terminal1) ==k1+1 or node2.index(element[n].terminal2) ==k1+1):
                    if element[n].name[0] =='R':
                        #if its R => resistance, and add 1/impedence for all
                        A[k2][k1] += 1/(float(element[n].value))
                    elif element[n].name[0] =='C':
                        #if its C => conductor
                        A[k2][k1] += complex(0,w*float(parsing[n][-1]))
                    elif element[n].name[0] =='L':
                        #if its L => inductor
                        A[k2][k1] += 1/complex(0,w*float(parsing[n][-1]))

        if k2!=k1 and k1 < num_nodes:       #filling in the places apart from the diagonals, same addition mechanism as above
            for n in range(len(parsing)):
                if (node2.index(element[n].terminal1) ==k1+1 and node2.index(element[n].terminal2) ==k2+1) or (node2.index(element[n].terminal1) ==k2+1 and node2.index(element[n].terminal2) ==k1+1):
                    if element[n].name[0] =='R':
                        A[k2][k1] -= 1/(float(element[n].value))
                    elif element[n].name[0] =='C':
                        A[k2][k1] -= complex(0,w*float(parsing[n][-1]))
                    elif element[n].name[0] =='L':
                        A[k2][k1] -= 1/complex(0,w*float(parsing[n][-1]))


        if k2 < num_nodes and k1 >= num_nodes:  #for the currents through the voltage sources
            for n in range(len(parsing)):
                if (element[n].name[0] == 'V'):
                    c1 = element[n].terminal1; c2 = element[n].terminal2
                    A[node2.index(element[n].terminal1)-1][int(int(element[n].name[1])+num_nodes-1)] = -1
                    A[node2.index(element[n].terminal2)-1][int(int(element[n].name[1])+num_nodes-1)] = +1



    if k2>= num_nodes:     #for the Voltage source equations
        for n in range(len(parsing)):
            if (element[n].name[0] == 'V') and (float(element[n].name[1]) == k2 - num_nodes +1):
                if int(node2.index(element[n].terminal2) - 1) !=-1:
                    A[k2][int(node2.index(element[n].terminal2) - 1)] = -1
                else:
                    A[k2][int(node2.index(element[n].terminal2) - 1)] = 0

                if int(node2.index(element[n].terminal1) - 1) !=-1:
                    A[k2][int(node2.index(element[n].terminal1) - 1)] = +1
                else:
                    A[k2][int(node2.index(element[n].terminal1) - 1)] = 0



for k1 in range(int(Mat_length)):   #filling in RHS matrix b
    if k1 < num_nodes:
        for n in range(len(parsing)):
            if element[n].name[0] =='I':
                if (node2.index(element[n].terminal1) ==k1+1):
                    B[k1][1] -= float(element[n].value)/2
                if (node2.index(element[n].terminal2) ==k1+1):
                    B[k1][1] += float(element[n].value)/2

    if k1 >= num_nodes:     #filling in b
        for n in range(len(parsing)):
            if element[n].name[0] =='V':
                if (int(element[n].name[1]) == k1 - num_nodes+1):
                    if parsing[n][3] ==('ac') or len(parsing[n]) > 4:
                        B[k1][0] = complex(float(parsing[n][-2])*math.cos(float(parsing[n][-1])),float(parsing[n][-2])*math.sin(float(parsing[n][-1])))/2
                        #we divide by 2 as this voltage is Vpp not Vmax
                    else:
                        B[k1][0] = float(parsing[n][3])

#print(node2)
print("Number of voltage sources are :{}\n".format(NumVolSource))
print("Matrix A is :\n{}\n".format(A))
print("Matrix B is :\n{}\n".format(B))

x = np.linalg.solve(A,B)
print('Output Matrix x is:\n{}\n'.format(x))

for i in range(0,int(num_nodes)):   #printing the node voltages
    if AC==0:
        print('V{} = {}'.format(i+1,np.real(x[i][0])))
    else:
        print('V{} = {} + {}j'.format(i+1, np.real(x[i][0]) , np.imag(x[i][0]) ))

if NumVolSource ==1:        #printing the value of the current through voltage sources, here if nuumber of voltage sources is equal to 1
    for i in range(int(num_nodes),int(num_nodes)+int(NumVolSource)):
        if AC==0:
            print('Current through V{} = {}'.format(i+1 - int(num_nodes),np.real(x[i][0])))
        else:
            print('Current through V{} = {} + {}j'.format(i+1 - int(num_nodes), np.real(x[i][0]) , np.imag(x[i][0]) ))

i = int(num_nodes);     #if the number of voltage sources is greater than 1
if NumVolSource !=1:
    if AC==0:
        print('Current through V{} = {}'.format(i+1 - int(num_nodes),np.real(x[i][0])))
    else:
        print('Current through V{} = {} + {}j'.format(i+1 - int(num_nodes), np.real(x[i][0]) , np.imag(x[i][0]) ))