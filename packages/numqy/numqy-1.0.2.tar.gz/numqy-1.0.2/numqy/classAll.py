"""
Given a string of characters, no more than 100 characters,
which may include brackets, numbers, letters,
punctuation marks and spaces, program to check whether
the (), [], {} in this string of characters match.
Input format:
Input gives a line of string in one line, no more than 100
characters, which may include brackets, numbers, letters, punctuation, and spaces.
Output format:
If the brackets are paired, output yes; otherwise, output No.

Input sample 1:
sin(10+20)
Output sample 1:
yes
"""

try:
    n = []
    flag = True
    symbol = input()
    for i in symbol:
        if i in '([{':
            n.append(i)
        elif i in ')]}':
            if n==[]:
                flag = False
            else:
                top = n.pop()
                if not '([{'.index(top)==')]}'.index(i):
                    flag=Flase
    if n==[] and flag:
        print("yes")
    else:
        print("no")
except:
    print("no")


"""
Assume that s and x represent the stack in and stack out operations respectively.
If an empty stack is operated according to a sequence 
consisting only of S and X, the corresponding operations are feasible 
(e.g. the stack is empty when there is no deletion) 
and the final state is empty, the sequence is called a legal stack operation 
sequence. Please write a program and input the s and X 
sequences to judge whether the sequence is legal.

Input format:
The first input line gives two positive integers n and m, 
where n is the number of sequences to be tested and m (≤ 50)
is the maximum capacity of the stack. Then n lines, 
each of which gives a sequence consisting only of S and X. 
The sequence is guaranteed not to be empty and its length does not exceed 100.
Output format:
For each sequence, output yes in one line if the sequence 
is a legal stack operation sequence, or no if it is not.

Input example:
4 10
SSSXXSXXSX
SSSXXSXXS
SSSSSSSSSSXSSXXXXXXXXXXX
SSSXXSXXX
Output example:
YES
NO
NO
NO
"""

a, b = map(int, input().split())
for i in range(a):
    num = 0
    zz = list(input())
    for i in range(len(zz)):
        if zz[i] == 'S' and num < b:
            num += 1
        elif zz[i] == "X" and num > 0:
            num -= 1
        else:
            num+=2
            break


    if i == len(zz)-1 and num == 0:
        print("YES")
    else:
        print("NO")

"""
Arithmetic expressions have prefix representation, 
infix representation and suffix representation. 
The commonly used arithmetic expression adopts infix representation, that is, 
the binary operator is located between two operands. 
Ask the designer to convert infix expressions to suffix expressions.
Input format:
Input the infix expression without spaces in one line,
which can contain +, -, *, \ and left and right 
parentheses (), and the expression shall not exceed 20 characters.
Output format:
The converted suffix expression is output in one line. 
Different objects (operands and symbols) are required to be
separated by spaces, but there must be no extra spaces at the end.

Input example:
2+3*(7-4)+8/4
Output example:
2 3 7 4 - * + 8 4 / +
"""

ans = []
stk = []
char_dict = {'+': 1, '-': 1, '*': 2, '/': 2, '(': 3, ')': 3}
s = input()
i = 0
while i < len(s):
    if (i < 1 or s[i - 1] == '(') and s[i] in ['+', '-'] or s[i].isdigit():
        tmp_s = ""
        if s[i] != '+':
            tmp_s += s[i]
        while i + 1 < len(s) and (s[i + 1] == '.' or s[i + 1].isdigit()):
            tmp_s += s[i + 1]
            i += 1
        ans.append(tmp_s)
    else:
        if s[i] == '(':
            stk.append(s[i])
        elif s[i] == ')':
            while stk and stk[-1] != '(':
                ans.append(stk.pop())
            stk.pop()
        else:
            while stk and stk[-1] != '(' and char_dict[stk[-1]] >= char_dict[s[i]]:
                ans.append(stk.pop())
            stk.append(s[i])
    i += 1
while stk:
    ans.append(stk.pop())
print(*ans)


"""
Please implement a myqueue class to realize outgoing, 
incoming, displaying the queue and calculating the queue length.
Implement the queue method push (int x); Implement the outgoing method pop(); 
Implement the queue length method size(); Implement the display queue method: show().
Input format:
Each input contains 1 test case.
The first line of each test case gives a positive integer n (n < = 10^6), and the next N lines 
have a number in each line, indicating an operation: 1 x: insert x from the end of the queue, 
0<=x<=2^31-1. 2: Indicates that the first element of the team is out of the team. 
3: Indicates the length of the queue. 4: Indicates that all elements in the queue are displayed.
Output format:
For action 1, add the element to be added to the end of the queue
For operation 2, if the queue is empty, "invalid" will be output; otherwise, 
the first element of the queue will be output and deleted from the queue.
For operation 3, output the queue length. Line wrap at the end of each output item.
For operation 4, each element in the output queue is separated by spaces, 
and there is no space after the last element.

Input example:
nine
1 23
1 34
three
four
two
1 56
two
three
1 90
Output example:
two
23 34
twenty-three
thirty-four
one
"""

n = []
for i in range(int(input())):
    oder = str(input()).split()
    if '1' == oder[0]:
        n.append(oder[1])
    elif '2' == oder[0]:
        if len(n)>0:
            print(n.pop(0))
        else:
            print("Invalid")
    elif '3' == oder[0]:
        print(len(n))
    else:
        print(' '.join(n))


"""
There are n people in a circle (numbered from 1 to n). Start counting 1, 2 and 3 from No. 1. 
Those who report 3 will quit. The next person will start counting from 1... 
Until there is only one person left. What is the original location of this person?
Input format:
There are multiple groups of test data, which are processed 
to the end of the file. Enter an integer n (5 ≤ n ≤ 100) for each set of tests.
Output format:
For each set of tests, output the number of the last person left.

Input example:
ten
twenty-eight
sixty-nine
Output example:
four
twenty-three 
sixty-eight
"""

n = []
try:
    while True:
        s = eval(input())
        for i in range(1,s+1):
            n.insert(0,i)
        i = 1
        while len(n)>1:
            num = n.pop()
            if i % 3 is not 0:
                n.insert(0,num)
            i+=1
        print(n.pop())
except:
    pass


"""
Suppose a bank has two business windows a and B, and the 
processing speed is different. The processing speed 
of window a is twice that of window B - that is, when 
window a processes two customers, 
window B processes one customer. Given the customer sequence 
arriving at the bank, please output 
the customer sequence in the order of business completion. 
It is assumed that the time interval when customers arrive 
successively is not considered, and when two customers are 
processed at the same time in different windows, 
the customers in window a will be output first.
Input format:
The input is a line of positive integers, in which the first 
number n (≤ 1000) is the total number of customers, 
followed by the number of n customers. Odd numbered 
customers need to go to window a for business, 
and even numbered customers need to go to window B. 
Numbers are separated by spaces.
Output format:
The customer number is output in the order of business processing completion. 
Numbers are separated by spaces, but there must be no extra spaces after the last number.

Input example:
8 2 1 3 9 4 11 13 15
Output example:
1 3 2 9 11 4 13 15
"""

aa=input().split()
AA=[]
BB=[]
cc=[]
for i in range(1,len(aa)):
    if int(aa[i])%2==0:
        BB.append(aa[i])
    else:
        AA.append(aa[i])
c=0
for i in range(len(aa)-1):
    if len(AA)!=0:
        cc.append(AA.pop(0))
        c=c+1
    if len(BB)!=0 and c%2==0:
        cc.append(BB.pop(0))
print(" ".join(cc))


"""
Read in n values and N integers, establish a single linked list and traverse the output.
Input format:
Read N and N integers.
Output format:
Outputs n integers separated by spaces (no spaces after the last number).
Input example:
Here is a set of inputs. For example:
two
10 5
Output example:
The corresponding output is given here. For example:
10 5
"""

try:
    n=input()
    s=input().split()
    print(" ".join(s))
except:
    pass


"""
Two non descending linked list sequences S1 and S2 are 
known, and a new non descending linked list S3 after 
S1 and S2 are combined is constructed by designing a function.
Input format:
The input is divided into two lines. Each line gives a non 
descending sequence composed of several positive integers, 
and − 1 represents the end of the sequence (− 1 does not 
belong to this sequence). Numbers are separated by spaces.
Output format:
Output the merged new non descending linked list in one row. 
The numbers shall be separated by spaces, 、
and there shall be no extra spaces at the end; If the new 
linked list is empty, null is output.

Input example:
1 3 5 -1
2 4 6 8 10 -1
Output example:
1 2 3 4 5 6 8 10
"""

lst = input().split()[:-1] + input().split()[:-1]
lst = list(map(int, lst))
if not lst:
    print('NULL')
else:
    lst.sort()
    for i in range(len(lst)):
        if i == len(lst) - 1:
            print(lst[i])
        else:
            print(lst[i], end=' ')


"""
Enter several integers no more than 100, establish a single 
linked list, and then reverse the link directions of 
all nodes in the linked list. It is required to still use the 
storage space of the original table. Output the inverted single linked list.
Input format:
First, enter an integer t to represent the number of groups of test data, 
and then t groups of test data. For each group of test data, 
input n numbers of data and N integers not exceeding 100 on one line.
Output format:
For each group of tests, output the inverted single linked list, 
leaving a space between each two data.

Input example:
one
11 55 50 45 40 35 30 25 20 15 10 5
Output example:
5 10 15 20 25 30 35 40 45 50 55
"""

i = int(input())
for j in range(i):
    n = input().split()
    s = []
    for jj in range(1,len(n)):
        s.append(n[jj])
    n = reversed(s)
    print(" ".join(n))

"""
Enter several integers no more than 100, establish a single linked list, 
and then reverse the link directions of all nodes in the linked list.
It is required to still use the storage space of the original table. 
Output the inverted single linked list.
Input format:
First, enter an integer t to represent the number of groups of test 
data, and then t groups of test data. For each group of test data, 
input n numbers of data and N integers not exceeding 100 on one line.
Output format:
For each group of tests, output the inverted single linked list, 
leaving a space between each two data.
Input example:
one
11 55 50 45 40 35 30 25 20 15 10 5
Output example:
51015250354045055 for a given binary tree, this problem requires 
you to output all leaf nodes from top to bottom and from left to right.
Input format:
First, the first line gives a positive integer n (≤ 10), which is 
the total number of nodes in the tree. The nodes in the tree are numbered 
from 0 to n − 1. Then n lines, each line gives a number of the 
left and right children of the corresponding node. If a child does not exist, 
a "-" will be given in the corresponding position. Numbers are separated by 1 space.
Output format:
Output the number of leaf nodes in a row in the specified order. 
The numbers shall be separated by 1 space, and there shall be no extra 
space at the beginning and end of the line.

Input example:
eight
1 -
- -
0 -
2 7
- -
- -
5 -
4 6
Output example:
4 1 5
"""

n=eval(input())
s={}
g=[str(x) for x in range(n)]
for i in range(n):
    s[str(i)]=input().split()
    for x in s[str(i)]:
        if x!='-':
            g.remove(x)
ans=[]
while g:
    temp=[]
    for x in g:
        if x=='-':
            continue
        l,r=s[x]
        if l=='-' and r=='-':
            ans.append(x)
        temp.append(l)
        temp.append(r)
    g=temp
print(' '.join(ans))


"""
Given the preorder traversal sequence and middle order traversal 
sequence of a binary tree, it is required to calculate the height of the 
binary tree.
Input format:
Input first gives a positive integer n (≤ 50), which is the total 
number of nodes in the tree. The following two lines give the preorder 
and middle order traversal sequences, which are strings of length n 
that do not contain repeated English letters (case sensitive).
Output format:
The output is an integer, that is, the height of the binary tree.
Input example:
nine
ABDFGHIEC
FDHGIBEAC
Output example:
5
"""

def createBT(preOrder, inOrder):
    if preOrder == "":return 0
    x=inOrder.find(preOrder[0])
    left = createBT(preOrder[1:x + 1], inOrder[:x])
    right = createBT(preOrder[x + 1:], inOrder[x + 1:])
    return left+1 if left>right else right+1
x=input()
print(createBT(input(),input()))


"""
5-1 post order traversal of binary tree 
This problem requires that the post order traversal of 
the binary tree be output. See the example for the output format.
"""

def postOrder(T):
    if T == None:
        return
    postOrder(T.left)
    postOrder(T.right)
    print(T.key, end=' ')


"""
5-2 Find the height of binary tree
This question requires the output of the height of the 
binary tree (the tree root is at the first level).
"""

def getHeight(T):
    if T== None:
        return 0
    l=getHeight(T.left)
    r=getHeight(T.right)
    if l+1>r+1:
        return l+1
    return r+1

"""
5-3 Hierarchical traversal of binary tree 
This problem requires the output of the hierarchical traversal 
of the binary tree. See the example for the output format.
"""


def layerOrder(T):
    q = Queue()
    q.push(T)
    while not q.isEmpty():
        s = q.pop()
        print(s.key, end=' ')
        if s.left != None: q.push(s.left)
        if s.right != None: q.push(s.right)


"""
5-4 Count the number of binary tree nodes 
This problem requires statistics of the number of binary tree nodes.
"""


def nodeCount(T):
    if T == None:
        return 0
    l = nodeCount(T.left)
    r = nodeCount(T.right)
    return r + l + 1


"""
5-5 Count the number of leaf nodes of binary tree 
This problem requires to calculate the number of leaves in 
the binary tree. See the example for the output format.
"""


def leafCount(T):
    if T == None:
        return 0
    if T.left == None and T.right == None:
        return 1

    l = leafCount(T.left)
    r = leafCount(T.right)
    return l + r


"""
6-1 Implementation of adjacency table of graph
Under the adjacency table storage structure of graph (based on vertex 
list and single linked list), this problem requires that the graph 
class implement two method functions def addvertex and def AddEdge 
"""

class arcnode:
    pass

class vexnode:
    pass

    # 代码填写部分
    def addVertex(self, vex_val):
        s = vexnode(vex_val)
        self.vex_list.append(s)
        self.vex_num = self.vex_num + 1


    def addEdge(self, f, t, cost=0):
        s = arcnode(t, cost, self.vex_list[f].first_arc)
        self.vex_list[f].first_arc = s
        s = arcnode(f, cost, self.vex_list[t].first_arc)
        self.vex_list[t].first_arc = s


"""
6-2 Depth first traversal of adjacency matrix storage graph 
This problem requires the implementation of a function to try to realize 
the depth first traversal of the adjacency matrix storage graph.
"""

def dfs(G,v):
    G.vis[v]=True
    print('',G.vertex[v],end='')
    for i in range(G.verNum):
        if G.edge[v][i]==1 and G.vis[i]==False:dfs(G,i)


"""
6-3 Find the degree of each vertex of an undirected graph using adjacency 
matrix as storage structure 
This problem requires the implementation of a function that outputs the 
values of the data elements of each vertex of the undirected graph 
and the degrees of each vertex.
"""


def printDegree(G):
    for i in range(G.verNum):
        gree=0
        for j in range(G.verNum):
            if G.edge[i][j]==1:gree=gree+1
        print(str(G.vertex[i])+':'+str(gree))


"""
6-4 Breadth first traversal of adjacency matrix storage graph 
This problem requires the implementation of a function to try to achieve 
the breadth first traversal of the adjacency matrix storage graph.
"""

def bfs(G,v):
    q=Queue()
    q.push(v)
    print('',G.vertex[v],end='')
    G.vis[v]=True
    while(not q.isEmpty()):
        s=q.pop()
        for i in range(G.verNum):
            if G.edge[s][i]==1 and G.vis[i]==False:
                 G.vis[i]=True
                 print('',G.vertex[i],end='')
                 q.push(i)

import numpy