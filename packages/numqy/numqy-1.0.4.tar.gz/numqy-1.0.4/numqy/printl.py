def numpy(zz):
    if zz == 'kuohaopipei':
        print("""
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
        """)
    if zz == "duizhancaozuo":
        print("""
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
        """)
    if zz == "biaodashizhuan":
        print("""
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
        """)
    if zz == "youguanduilie":
        print("""
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
        """)
    if zz == "yuesefuhuan":
        print("""
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

""")
    if zz == "yinhangyewu":
        print("""
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
""")
    if zz == "danlianbiaode":
        print("""
try:
    n=input()
    s=input().split()
    print(" ".join(s))
except:
    pass   
""")
    if zz == "lianggeyouxv":
        print("""
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

        """)
    if zz == "lianbiaodeni":
        print("""
i = int(input())
for j in range(i):
    n = input().split()
    s = []
    for jj in range(1,len(n)):
        s.append(n[jj])
    n = reversed(s)
    print(" ".join(n))
        """)
    if zz == "liechuyejie":
        print("""
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
        """)
    if zz == "huanyuanercha":
        print("""
def createBT(preOrder, inOrder):
    if preOrder == "":return 0
    x=inOrder.find(preOrder[0])
    left = createBT(preOrder[1:x + 1], inOrder[:x])
    right = createBT(preOrder[x + 1:], inOrder[x + 1:])
    return left+1 if left>right else right+1
x=input()
print(createBT(input(),input()))
        """)
    if zz == "postOrder":
        print("""
def postOrder(T):
    if T == None:
        return
    postOrder(T.left)
    postOrder(T.right)
    print(T.key, end=' ')
        """)
    if zz == "getHeight":
        print("""
def getHeight(T):
    if T== None:
        return 0
    l=getHeight(T.left)
    r=getHeight(T.right)
    if l+1>r+1:
        return l+1
    return r+1
        """)
    if zz == "LayerOrder":
        print("""
def layerOrder(T):
    q = Queue()
    q.push(T)
    while not q.isEmpty():
        s = q.pop()
        print(s.key, end=' ')
        if s.left != None: q.push(s.left)
        if s.right != None: q.push(s.right)
        """)
    if zz == "nodeCount":
        print("""
def nodeCount(T):
    if T == None:
        return 0
    l = nodeCount(T.left)
    r = nodeCount(T.right)
    return r + l + 1
        """)
    if zz == "leafCount":
        print("""
def leafCount(T):
    if T == None:
        return 0
    if T.left == None and T.right == None:
        return 1

    l = leafCount(T.left)
    r = leafCount(T.right)
    return l + r
        """)
    if zz == "addVertex":
        print("""
    def addVertex(self, vex_val):
        s=vexnode(vex_val)
        self.vex_list.append(s)
        self.vex_num+=1

    def addEdge(self, f, t, cost=0):
        s=arcnode(t,cost,self.vex_list[f].first_arc)
        self.vex_list[f].first_arc=s
        s=arcnode(f,cost,self.vex_list[t].first_arc)
        self.vex_list[t].first_arc=s
        """)
    if zz == "dfs":
        print("""
def dfs(G,v):
    G.vis[v]=True
    print('',G.vertex[v],end='')
    for i in range(G.verNum):
        if G.edge[v][i]==1 and G.vis[i]==False:
            dfs(G,i)
        """)
    if zz == "printDegree":
        print("""
def printDegree(G):
    for i in range(G.verNum):
        g=0
        for j in range(G.verNum):
            if G.edge[i][j]==1:
                g+=1
        print(str(G.vertex[i])+':'+str(g))
        """)
    if zz == "bfs":
        print("""
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

""")


x = input()
numpy(x)
print('successly')
