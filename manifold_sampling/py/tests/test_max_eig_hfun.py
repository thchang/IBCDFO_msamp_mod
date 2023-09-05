import itertools
import sys

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist

sys.path.append("../")
sys.path.append("../h_examples/")
from manifold_sampling_primal import manifold_sampling_primal
from matrix_Ffuns import Ffun_default, Ffun_sort, compute_M_and_eig, Ffun_mattrix
from pw_maximum import pw_maximum as hfun
from pw_maximum_eig import pw_maximum_eig as hfun2

n = 10
AllX = np.empty((0, n))
AllEigVecs = {}
count = 0


def Ffun_fast_sort(y):
    global AllX, AllEigVecs, count
    eigvals, eigvecs = compute_M_and_eig(y)

    if len(AllX):
        ind_of_closest_past_point = np.argmin(np.linalg.norm(AllX - y, axis=1))
        last_eig_vecs = AllEigVecs[ind_of_closest_past_point]
        v = np.conjugate(np.transpose(eigvecs)) @ last_eig_vecs
        b = np.argsort(v, axis=0)
        best_perm = b[-1, :]
        assert len(np.unique(best_perm)) == len(best_perm)

        # print(best_perm)
        # print(len(np.unique(best_perm)))
        eigvals = eigvals[list(best_perm)]
        eigvecs = eigvecs[:, best_perm]

    AllX = np.vstack((AllX, y))
    AllEigVecs[count] = eigvecs
    count += 1

    return eigvals


def Ffun_slow_sort2(y):
    global AllX, AllEigVecs, count
    eigvals, eigvecs = compute_M_and_eig(y)

    if len(AllX):
        ind_of_closest_past_point = np.argmin(np.linalg.norm(AllX - y, axis=1))
        last_eig_vecs = AllEigVecs[ind_of_closest_past_point]

        alldists = cdist(eigvecs.T, last_eig_vecs.T)

        row_ind, col_ind = linear_sum_assignment(alldists)

        eigvals = eigvals[col_ind]
        eigvecs = eigvecs[:, col_ind]

    AllX = np.vstack((AllX, y))
    AllEigVecs[count] = eigvecs
    count += 1

    return eigvals


def Ffun_all_perms(y):
    global AllX, AllEigVecs, count
    eigvals, eigvecs = compute_M_and_eig(y)

    if len(AllX):
        ind_of_closest_past_point = np.argmin(np.linalg.norm(AllX - y, axis=1))
        last_eig_vecs = AllEigVecs[ind_of_closest_past_point]

        best_dist = np.inf
        for p in itertools.permutations(np.arange(len(eigvals))):
            this_perm_dist = np.linalg.norm(eigvecs[:, p] - last_eig_vecs)
            if this_perm_dist < best_dist:
                best_dist = this_perm_dist
                best_perm = p

        eigvals = eigvals[list(best_perm)]
        eigvecs = eigvecs[:, best_perm]

    AllX = np.vstack((AllX, y))
    AllEigVecs[count] = eigvecs
    count += 1

    return eigvals


nfmax = 80
subprob_switch = "linprog"
LB = -1 * np.ones((1, n))
UB = np.ones((1, n))
x0 = np.ones((1, n))
# x0 = np.array([(-1)**(i) for i in range(n)])
# x0 = np.array([(-1)**(i+1) for i in range(10)])

X, F, h, xkin, flag = manifold_sampling_primal(hfun, Ffun_default, x0, LB, UB, nfmax, subprob_switch)
plt.plot(h, linewidth=6, alpha=0.8, solid_joinstyle="miter", label="Default")

X, F, h, xkin, flag = manifold_sampling_primal(hfun, Ffun_sort, x0, LB, UB, nfmax, subprob_switch)
plt.plot(h, linewidth=6, alpha=0.8, solid_joinstyle="miter", label="Sorted")


# plt.plot(F, linewidth=6, alpha=0.8, solid_joinstyle='miter')
# plt.plot(F, linewidth=6, alpha=0.8)
# plt.savefig("Initial.png", dpi=300, bbox_inches="tight")
# plt.close()
# X, F, h, xkin, flag = manifold_sampling_primal(hfun, Ffun_all_perms, x0, LB, UB, nfmax, subprob_switch)
# plt.plot(h, linewidth=6, alpha=0.8, solid_joinstyle='miter', label="Complete search mapping")

X, F, h, xkin, flag = manifold_sampling_primal(hfun, Ffun_slow_sort2, x0, LB, UB, nfmax, subprob_switch)
plt.plot(h, linewidth=6, alpha=0.8, solid_joinstyle="miter", label="Hopefully smarter mapping")

X, F, h, xkin, flag = manifold_sampling_primal(hfun, Ffun_all_perms, x0, LB, UB, nfmax, subprob_switch)
plt.plot(h, linewidth=6, alpha=0.8, solid_joinstyle="miter", label="All permutations")

X, F, h, xkin, flag = manifold_sampling_primal(hfun2, Ffun_mattrix, x0, LB, UB, nfmax, subprob_switch)
plt.plot(h, linewidth=6, alpha=0.8, solid_joinstyle="miter", label="Matt")


plt.legend()
plt.savefig("Initial.png", dpi=300, bbox_inches="tight")
