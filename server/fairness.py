import numpy as np
from sympy import symbols, Eq, nsolve

M = [[-3.035, -0.5061, 1.022], [-4.85, -0.647, 1.011], [-17.53, -1.048, 0.9912]]


# a vector of res=[] and r_max=[] is needed!
def stage1(N, M, res, r_max, BW):
    u = []
    r = list(symbols('r0:%d' % N))
    # print("vector of r= ", r)
    for i in range(N):
        if res[i] == 1080:
            a = M[0][0]
            b = M[0][1]
            c = M[0][2]
            frac = a * (r_max[i] ** b) + c
            u.append((a * (r[i] ** b) + c) / frac)
        elif res[i] == 720:
            a = M[1][0]
            b = M[1][1]
            c = M[1][2]
            frac = a * (r_max[i] ** b) + c
            u.append((a * (r[i] ** b) + c) / frac)
        elif res[i] == 360:
            a = M[2][0]
            b = M[2][1]
            c = M[2][2]
            frac = a * (r_max[i] ** b) + c
            u.append((a * (r[i] ** b) + c) / frac)
    # print(u)
    eq2 = Eq(sum(r), BW)
    eq = []
    eq.append(eq2)
    for i in range(N - 1):
        e1 = u[i] - u[i + 1]
        eq.append(Eq(e1, 0))
    # print("vector of equations= ", eq)
    ov = np.ones(N)
    sol = nsolve(eq, r, ov)
    # print("optimal r= ", sol)
    return sol


def stage3(M, CL, t, ti, r_prime):
    w = 1 / 3
    VQ_F1 = []
    CT_F1 = []
    SI_F1 = []
    for r in CL:
        VQ_F = VQ_fairness(M, r)
        VQ_F1.append(VQ_F)
        CT_F = CT_fairness(M, r)
        CT_F1.append(CT_F)
        SI_F = SI_fairness(M, r, t, ti, r_prime)
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


def U_Prime(N, M, r, res, r_max):
    u_prime_vector = []
    for i in range(N):
        if res[i] == 1080:
            a = M[0][0]
            b = M[0][1]
            c = M[0][2]
            frac = a * (r_max[i] ** b) + c
            u_prime_vector.append((a * (r[i] ** b) + c) / frac)
        elif res[i] == 720:
            a = M[1][0]
            b = M[1][1]
            c = M[1][2]
            frac = a * (r_max[i] ** b) + c
            u_prime_vector.append((a * (r[i] ** b) + c) / frac)
        elif res[i] == 360:
            a = M[2][0]
            b = M[2][1]
            c = M[2][2]
            frac = a * (r_max[i] ** b) + c
            u_prime_vector.append((a * (r[i] ** b) + c) / frac)
    return u_prime_vector


def Q(N, M, r, res):
    Q_vector = []
    for i in range(N):
        if res[i] == 1080:
            a = M[0][0]
            b = M[0][1]
            c = M[0][2]
            Q_vector.append(a * (r[i] ** b) + c)
        elif res[i] == 720:
            a = M[1][0]
            b = M[1][1]
            c = M[1][2]
            Q_vector.append(a * (r[i] ** b) + c)
        elif res[i] == 360:
            a = M[2][0]
            b = M[2][1]
            c = M[2][2]
            Q_vector.append(a * (r[i] ** b) + c)
    return Q_vector


def VQ_fairness(N, M, r, res):
    Q1 = Q(N, M, r, res)
    s_vq = np.std(Q1)
    RSD = (100 * s_vq) / np.mean(Q1)
    return RSD


def CT_fairness(N, M, res, r, r_max):
    utility = U_Prime(N, M, r, res, r_max)
    CT = np.sum(r) / np.sum(utility)
    return CT


def SI_fairness(N, M, res, r, t, ti, r_prime, res2):
    # r_prime is a vector of projected bitrates
    # and res2 is a vector of resolution after the switching
    Q1 = Q(N, M, r, res)
    Q_prime = []  # vector of qualities after switching
    for i in range(N):
        if res2[i] == 1080:
            a = M[0][0]
            b = M[0][1]
            c = M[0][2]
            Q_prime.append(a * (r_prime[i] ** b) + c)
        elif res2[i] == 720:
            a = M[1][0]
            b = M[1][1]
            c = M[1][2]
            Q_prime.append(a * (r_prime[i] ** b) + c)
        elif res2[i] == 360:
            a = M[2][0]
            b = M[2][1]
            c = M[2][2]
            Q_prime.append(a * (r_prime[i] ** b) + c)
    del_Q = []
    S1 = []
    S2 = []
    for i in len(ti):
        del_Q[i] = abs(Q1[i] - Q_prime[i])
        S1[i] = del_Q[i] * np.exp(-0.015 * (t - ti(i)))
        S2.append(max(S1[i], 0.1 * del_Q[i]))
    s_si = np.std(S2)
    RSD = (100 * s_si) / np.mean(s_si)
    return RSD
