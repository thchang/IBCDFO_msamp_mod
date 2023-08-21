import numpy as np


def max_sum_beta_plus_const_viol(z, H0=None):
    # This the outer h function required by manifold sampling.
    # If z \in R^p
    # It encodes the objective
    #    max_{i = 1,...,p1} z_i + alpha *sum_{i = p1+1}^{p} max(z_i, 0)^2
    #
    # Hashes are output (and must be input) in the following fashion:
    #   Hash elements are strings of p integers.
    #     0 in position 1 <= i <= p1 means max_{i = 1,...,p1} z_i > z_i
    #     1 in position 1 <= i <= p1 means max_{i = 1,...,p1} z_i = z_i
    #     0 in position p1+1 <= i <= p means max(z_i,0) = 0
    #     1 in position p1+1 <= i <= p means max(z_i,0) = z_i
    #
    #   Similarly, if H0 has a 1 in position i uses z_i in the calculation of h and grads.

    p = len(z)
    alpha = 0
    p1 = p

    if H0 is None:
        h1 = np.max(z[:p1])
        h2 = alpha * np.sum(np.maximum(z[p1:], 0) ** 2)
        h = h1 + h2

        atol = 1e-8
        rtol = 1e-8
        inds1 = np.where(np.abs(h1 - z[:p1]) <= atol + rtol * np.abs(z[:p1]))[0]

        inds2 = p1 + np.where(z[p1:] >= -rtol)[0]

        grads = np.zeros((p, len(inds1)))

        Hashes = []
        for j in range(len(inds1)):
            hash_str = "0" * p
            hash_str = hash_str[: inds1[j]] + "1" + hash_str[inds1[j] + 1 :]
            hash_str = hash_str[: inds2[j]] + "1" + hash_str[inds2[j] + 1 :]
            Hashes.append(hash_str)
            grads[inds1[j], j] = 1
            grads[inds2, j] = alpha * 2 * z[inds2]

        return h, grads, Hashes
    else:
        J = len(H0)
        h = np.zeros(J)
        grads = np.zeros((p, J))

        for k in range(J):
            max_ind = np.where(np.array(list(H0[k])[:p1]) == "1")[0]
            assert len(max_ind) == 1, "I don't know what to do in this case"
            grads[max_ind, k] = 1

            h1 = z[max_ind]

            const_viol_inds = p1 + np.where(np.array(list(H0[k])[p1:]) == "1")[0]
            if len(const_viol_inds) == 0:
                h2 = 0
            else:
                grads[const_viol_inds, k] = alpha * 2 * z[const_viol_inds]
                h2 = alpha * np.sum(np.maximum(z[const_viol_inds], 0) ** 2)
            h[k] = h1 + h2

        return h, grads
