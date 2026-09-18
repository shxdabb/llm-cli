# class Solution:
#     def generateParenthesis(self, n: int) -> List[str]:
        


    #stack = [] ; o = 2 c = 2
curr = []
res = []

def dfs(o,c,curr):

    if not o and not c:
        res.append(curr[:])
        return
    
    if o and o <= c:
        curr.append('(')
        dfs(o-1,c,curr)
    if o < c:
        curr.append(')')
        dfs(o,c-1,curr)

    if curr and curr.pop() == '(':

        return (o+1,c,curr)

    else:

        return (o,c+1,curr)

dfs(3,3,curr)

print(res)

 
            
            
