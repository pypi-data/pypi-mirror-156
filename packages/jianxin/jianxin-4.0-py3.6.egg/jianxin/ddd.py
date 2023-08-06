def numpy(zz):
    if zz=='kuohaopipei':
        print("""
try:
    bb=[]
    zhengwu='yes'
    a=list(input())
    for i in a:
        if i=='[' or i=='{' or i=='(':
            bb.append(i)
        elif i=='}' or i==']' or i==')':
            if (bb[-1]=='{'and i=='}') or (bb[-1]=='['and i==']') or (bb[-1]=='('and i==')'):
                del bb[-1]
            else:
                zhengwu='no'
    if len(bb)!=0:
        zhengwu='no'
    print(zhengwu)
except:
    print('no')
        """)
    if zz=="duizhancaozuo":
        print("""
c,f= map(int, input().split())
for k in range(c):
    zhengwu='YES'
    bb=[]
    a=list(input())
    for i in a:
        if len(bb)>int(f):
            zhengwu='NO'
            break
        if i=='S':
            bb.append(i)
        else:
            if len(bb)==0:
                zhengwu='NO'
                break
            del bb[-1]
    if len(bb)!=0:
        zhengwu='NO'
    print(zhengwu)
        """)
    if zz=="biaodashizhuan":
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
    if zz=="youguanduilie":
        print("""
bb=[]
x=int(input())
for i in range(x):
    order=input().split()
    if order[0]=='1':
        bb.append(order[1])
    if order[0]=='2':
        if len(bb)==0:
            print('Invalid')
        else:
            print(bb[0])
            del bb[0]
    if order[0]=='3':
        print(len(bb))
    if order[0]=='4':
        print(" ".join(bb))
        """)
    if zz=="yuesefuhuan":
        print("""
n=[]
try:
    while True:
        a=int(input())
        for i in range(1,a+1):
            n.insert(0,i)
        i=1
        while len(n)>1:
            zhi=n.pop()
            if i%3 !=0:
                n.insert(0,zhi)
            i=i+1
        print(n.pop())
except:
    pass       
""")
    if zz=="yinhangyewu":
        print("""
aa=input().split()
AA=[]
BB=[]
CC=[]
for i in range(1,len(aa)):
    if int(aa[i])%2==0:
        BB.append(aa[i])
    else:
        AA.append(aa[i])
c=0
for i in range(1,len(aa),1):
    if len(AA)!=0:
        CC.append(AA[0])
        del AA[0]
        c=c+1
    if (len(BB)!=0 and c%2==0):
        CC.append(BB[0])
        del BB[0]
print(" ".join(CC))        
""")
    if zz=="lianggeyouxu":
        print("""
lst=input().split()[:-1]+input().split()[:-1]
lst=list(map(int,lst))
if lst==[]:
    print('NULL')
else:
    lst.sort()
    lst=[str(i) for i in lst]
    print(" ".join(lst))
    """)
    if zz=="lianbiaodeni":
        print("""
t=int(input())
while(t):
    t=t-1
    a=input().split()[1:]
    a.reverse()
    print(" ".join(a))        
""")
    if zz=="liechuyejie":
        print("""
class Node:
    def __init__(self,data):
        self.data=data
        self.left=None
        self.right=None
n=int(input())
nodes=[-1]*n
parent=[-1]*n
lchi=[]
rchi=[]
lst=[]
for i in range(n):
    u,v=input().split()
    lst.append((u,v))
    if u!='-':
        lchi.append(int (u))
    else:
        lchi.append(u)
    if v!='-':
        rchi.append(int(v))
    else:
        rchi.append(v)
for i in range(n):
    if i not in lchi and i not in rchi:
        root=i
        break
inx=0
def creat(root):
    global inx
    if inx==n:
        return
    node = Node(root)
    inx+=1
    if (lchi[root]!='-'):
        node.left=creat(lchi[root])
    if rchi[root]!='-':
        node.right=creat(rchi[root])
    return node
rot=creat(root)
lst4=[]
def BFS(root):
    if root == None:
        return
    queue = []
    queue.append(root)
    while queue:
        now_node = queue.pop(0)
        if now_node.left==None and now_node.right==None:
            lst4.append(str(now_node.data))
        if now_node.left != None:
            queue.append(now_node.left)
        if now_node.right != None:
            queue.append(now_node.right)
BFS(rot)
print(' '.join(lst4))
        """)
    if zz=="huanyuanercha":
        print("""
class BinaryTree:
    def __init__(self, newValue):
        self.key = newValue
        self.left = None
        self.right = None
        pass
    def insertLeft(self, newNode):
        if isinstance(newNode, BinaryTree):
            self.left = newNode
        else:
            p = BinaryTree(newNode)
            p.left = self.left
            self.left = p
    def insertRight(self, newNode):
        if isinstance(newNode, BinaryTree):
            self.right = newNode
        else:
            p = BinaryTree(newNode)
            p.right = self.right
            self.right = p
    def getLeft(self):
         return self.left
    def getRight(self):
        return self.right
    def setRoot(self, newValue):
        self.key = newValue
    def getRoot(self):
        return self.key
def GetHeight(BT):
    h1 = 1
    h2 = 1
    if BT.getLeft() or BT.getRight():
        try:
            h1 += GetHeight(BT.getLeft())
        except:
            pass
        try:
            h2 += GetHeight(BT.getRight())
        except:
            pass
        return h1 if h1 > h2 else h2
    else:
        return 1
def preInTree(preOrder, inOrder):
    if preOrder == "":
        return
    T = BinaryTree(preOrder[0])
    n, r = len(inOrder), 0
    for i in range(n):
        if inOrder[i] == preOrder[0]:
            r = i
            break
    T.left = preInTree(preOrder[1: r + 1], inOrder[0: r])
    T.right = preInTree(preOrder[r + 1:], inOrder[r + 1:])
    return T
n = int(input())
preOrder = input()
inOrder = input()
T = preInTree(preOrder, inOrder)
print(GetHeight(T))
def createBT(preOrder, inOrder):
    if preOrder == "":return 0
    x=inOrder.find(preOrder[0])
    left = createBT(preOrder[1:x + 1], inOrder[:x])
    right = createBT(preOrder[x + 1:], inOrder[x + 1:])
    return left+1 if left>right else right+1
x=input()
print(createBT(input(),input()))
        """)
    if zz=="erchashudecengxubianli":
        print("""
def layerOrder(T):
    q=Queue()
    q.push(T)
    while not q.isEmpty():
        s=q.pop()
        print(s.key,end=' ')
        if s.left!=None:
            q.push(s.left)
        if s.right!=None:
            q.push(s.right)
        """)
    if zz=="tudelingjiebiao":
        print("""
    def addVertex(self, vex_val):
        s=vexnode(vex_val)
        self.vex_list.append(s)
        self.vex_num=self.vex_num+1

    def addEdge(self, f, t, cost=0):
        s=arcnode(t,cost,self.vex_list[f].first_arc)
        self.vex_list[f].first_arc=s
        s=arcnode(f,cost,self.vex_list[t].first_arc)
        self.vex_list[t].first_arc=s
        """)
    if zz=="tu":
        print("""
    #图的邻接表的实现python版
    def addVertex(self, vex_val):
        s=vexnode(vex_val)
        self.vex_list.append(s)
        self.vex_num=self.vex_num+1

    def addEdge(self, f, t, cost=0):
        s=arcnode(t,cost,self.vex_list[f].first_arc)
        self.vex_list[f].first_arc=s
        s=arcnode(f,cost,self.vex_list[t].first_arc)
        self.vex_list[t].first_arc=s
        
邻接矩阵存储图的深度优先遍历（Python语言描述）
def dfs(G,v):
    G.vis[v]=True
    print('',G.vertex[v],end='')
    for i in range(G.verNum):
        if G.edge[v][i]==1 and G.vis[i]==False:
            dfs(G,i)
            
求采用邻接矩阵作为存储结构的无向图各顶点的度（Python语言描述）
def printDegree(G):
    for i in range(G.verNum):
        gree=0
        for k in range(G.verNum):
            if G.edge[i][k]==1:
                gree+=1
        print("{}:{}".format(G.vertex[i],gree))
        
邻接矩阵存储图的广度优先遍历（Python语言描述）
#顶点v(编号)出发对图G进行广度优先遍历
def bfs(G,v):
    q=Queue()
    q.push(v)
    G.vis[v]=True
    print('',G.vertex[v],end='')
    while not q.isEmpty():
        s=q.pop()
        for i in range(G.verNum):
            if G.edge[s][i]==1 and G.vis[i]==False:
                print('',G.vertex[i],end='')
                q.push(i)
                G.vis[i]=True
        
""")
x=input()
numpy(x)
