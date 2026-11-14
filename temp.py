# # class Solution:
# #     def generateParenthesis(self, n: int) -> List[str]:
        


#     #stack = [] ; o = 2 c = 2
# curr = []
# res = []

# def dfs(o,c,curr):

#     if not o and not c:
#         res.append(curr[:])
#         return
    
#     if o and o <= c:
#         curr.append('(')
#         dfs(o-1,c,curr)
#     if o < c:
#         curr.append(')')
#         dfs(o,c-1,curr)

#     if curr and curr.pop() == '(':

#         return (o+1,c,curr)

#     else:

#         return (o,c+1,curr)

# dfs(3,3,curr)

# print(res)

 
            
            
# graph = {
#     0: [1, 2],
#     1: [0, 3],
#     2: [0],
#     3: [1]
# }
# visited = set()

# def dfs(node):
#     if node in visited:
#         return
#     visited.add(node)
#     print(node)

#     for nodes in graph[node]:
#         dfs(nodes)

# dfs(0)


# graph2 = [
#     [0,1,1,0],
#     [1,0,0,1],
#     [1,0,0,0],
#     [0,1,0,0]
# ]

# visited = set()

# def dfs(node):
#     if node in visited:
#         return
#     print(node)
#     visited.add(node)

#     for nodes in range(len(graph2)):
#         if graph2[node][nodes] == 1 and nodes not in visited:
#             dfs(nodes)

# dfs(1)

# graph = {
#     0: [1],
#     1: [0],
#     2: [3],
#     3: [2],
#     4: []
# }

# visited = set()
# def dfs(node):
    
#     visited.add(node)

#     for nodes in graph[node]:
#         if nodes not in visited:
#             dfs(nodes)

# count = 0
# for node in graph:
#     if node not in visited:
#         count+=1
#         dfs(node)
# print(count)


graph = [
    [2, 4],
    [1, 3],
    [2, 4],
    [1, 3]
]

def dfs(node):
    if node in visited:
        return
    visited.add(node)
    print(node)
    for nei in graph[node-1]:
        dfs(nei)


visited = set()
dfs(1)
