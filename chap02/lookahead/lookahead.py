##################################################################
'''
compute_lookahead_sets:
given a grammar as a list of tuples this function will return a grammar
enriched with the lookahead sets.

for example, the grammar,

exp : + exp exp
    | - exp exp
    | x
    | y
    | z

is represented as,

[('exp',['+','exp','exp']),
 ('exp',['-','exp','exp']),
 ('exp',['x']),
 ('exp',['y']),
 ('exp',['z'])]

 and with lookahead sets it becomes,

 [('exp', {'+'}, ['+', 'exp', 'exp']),
  ('exp', {'-'}, ['-', 'exp', 'exp']),
  ('exp', {'x'}, ['x']),
  ('exp', {'y'}, ['y']),
  ('exp', {'z'}, ['z'])]

'''
##################################################################
def first_symbol(rule_body):
    return rule_body[0]

##################################################################
def nonterminal_set(G):
    nt = set()
    for r in G:
        if len(r) == 2:
            (A, B) = r
        else:
            (A, L, B) = r
        nt.add(A)
    return nt

##################################################################
def terminal_set(G):
    nt = nonterminal_set(G)
    symbols = []
    for r in G:
        if len(r) == 2:
            (A, B) = r
        else:
            (A, L, B) = r
        symbols.extend(B)
    t = set(symbols) - nt
    return t

##################################################################
def lookahead_set(N, G):
    '''
    Accepts: N is a nonterminal in G
    Accepts: G is a context-free grammar
    Returns: L is a lookahead set
    '''
    L = set()
    for R in G:
        (A, rule_body) = R
        if A == N:
            Q = first_symbol(rule_body)
            if Q == "":
                raise ValueError("nonterminal {} is a nullable prefix"
                                 .format(A))
            elif Q in terminal_set(G):
                L = L | set([Q])
            elif Q in nonterminal_set(G):
                L = L | lookahead_set(Q, G)
    return L

##################################################################
def compute_lookahead_sets(G):
    '''
    Accepts: G is a context-free grammar viewed as a list of rules
    Returns: GL is a context-free grammar extended with lookahead sets
    '''
    GL = []
    for R in G:
        (A, rule_body) = R
        S = first_symbol(rule_body)
        if S == "":
            GL.append((A, set([""]), rule_body))
        elif S in terminal_set(G):
            GL.append((A, set([S]), rule_body))
        elif S in nonterminal_set(G):
            L = lookahead_set(S,G)
            GL.append((A, L, rule_body))
    return GL

##################################################################
def check_dup_lookahead(GL):
    '''
    Accepts: GL is a context-free grammar extended with lookahead sets
    Returns: GL
    Throws an exception if the lookahead set for a rule
    appears more than once for a particular nonterminal
    '''
    nonterms = {}
    for R in GL:
        (A, L, rule_body) = R
        if A not in nonterms.keys():
            nonterms[A] = [e for e in L]
        else:
            for e in L:
                if e not in nonterms[A]:
                    nonterms[A].append(e)
                else:
                    raise ValueError("common prefix {} for nonterminal {}"
                                     .format(e,A))
    return GL

##################################################################
if __name__ == "__main__":
    from sys import stdin
    import pprint
    pp = pprint.PrettyPrinter()
    try:
        grammar = eval(stdin.read())
        pp.pprint(check_dup_lookahead(compute_lookahead_sets(grammar)))
    except Exception as e:
        print("Error: " + str(e))
