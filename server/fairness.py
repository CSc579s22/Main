import numpy as np
from sympy import symbols, Eq, solve


def stage1(N, a, b, c, r_max, BW):  # r_max is an integer
    r = []
    eqs = []
    r = list(symbols('r0:%d' % N))
    # print(r)
    for i in range(N):
        if i == N - 1:
            break
        else:
            eqs.append(Eq(((a * (r[i] ** b) + c) / (a * (r_max ** b) + c)) - (
                        (a * (r[i + 1] ** b) + c) / (a * (r_max ** b) + c)), 0))
    # print(eqs)
    sol = solve(eqs)
    # print(sol)
    r1 = BW / N
    # print(r1)
    opt_r = []
    for i in range(N):
        opt_r.append(r1)
    return sol, opt_r


# r= stage1(5,-3,-0.5,1,30,50)
# print(r)

def stage3(a, b, c, CL, t, ti, r_prim):
    w = 1 / 3
    VQ_F1 = []
    CT_F1 = []
    SI_F1 = []
    for r in CL:
        VQ_F = VQ_fairness(a, b, c, r)
        VQ_F1.append(VQ_F)
        CT_F = CT_fairness(a, b, c, r)
        CT_F1.append(CT_F)
        SI_F = SI_fairness(a, b, c, r, t, ti, r_prim)
        SI_F1.append(SI_F)
    VQ_MAX = max(VQ_F1)
    CT_MAX = max(CT_F1)
    SI_MAX = max(SI_F1)
    VQ_F2 = []
    CT_F2 = []
    SI_F2 = []
    for i in VQ_F1:
        x = i / VQ_MAX
        x = w * x
        VQ_F2.append(x)
    for j in CT_F1:
        y = j / CT_MAX
        y = w * y
        CT_F2.append(y)
    for k in SI_F1:
        z = k / SI_MAX
        z = w * z
        SI_F2.append(z)
    S = []
    for n in len(CL):
        v = VQ_F2[n] + CT_F2[n] + SI_F2[n]
        S.append(v)
    S_combined = min(S)
    return S_combined


# resolution is fixed
def U_Prim(N, a, b, c, r, r_max):
    U_max = a * (r_max) ** b + c
    for i in range(N):
        U = (a * (r[i]) ** b) + c
        U_prim = U / U_max

    return U_prim


# vq_utiliy= U_Prim(4,-3.035,-0.5061,1.022,[12,14,18,22],30)
# print(vq_utiliy)

def Q(a, b, c, r):
    Q = []
    for i in r:
        Q.append(a * (i ** b) + c)
    return Q


# q=Q(-3.035,-0.5061,1.022,[12,14,18,22])
# print(q)

def VQ_fairness(a, b, c, r):
    Q1 = Q(a, b, c, r)
    s_vq = np.std(Q1)
    RSD = (100 * s_vq) / np.mean(Q1)
    return RSD


# f= VQ_fairness(-3.035,-0.5061,1.022,[12,14,18,22])
# print(f)

def CT_fairness(N, a, b, c, r, r_max):
    utility = U_Prim(N, a, b, c, r, r_max)
    CT = np.sum(r) / np.sum(utility)
    return CT


# c=CT_fairness(4,-3.035,-0.5061,1.022,[12,14,18,22],30)
# print(c)


def SI_fairness(a, b, c, r, t, ti, r_prim):
    Q1 = Q(a, b, c, r)
    Q_prim = a * (r_prim ** b) + c
    del_Q = []
    S1 = []
    S2 = []
    for i in len(ti):
        del_Q[i] = abs(Q1[i] - Q_prim[i])
        S1[i] = del_Q[i] * np.exp(-0.015 * (t - ti(i)))
        S2[i] = max(S1[i], 0.1 * del_Q[i])
    s_si = np.std(S2)
    RSD = (100 * s_si) / np.mean(s_si)
    return RSD
