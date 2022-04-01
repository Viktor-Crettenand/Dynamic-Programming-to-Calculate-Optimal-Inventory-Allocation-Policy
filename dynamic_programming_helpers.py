import numpy as np
import pandas as pd

class DynamicProgram():

    def __init__(self, T, n_init, Q, pi_0, pi_b, r_b, pi_p, r_p, h, c_b, c_p, s_p, salvage, mode = 'joint', *args):
        self.T = T.copy()
        self.n_init = n_init
        self.Q = Q.copy()
        self.pi_0 = pi_0
        self.pi_b = pi_b
        self.r_b = r_b
        self.pi_p = pi_p
        self.r_p = r_p
        if args:
            self.joint = args[0]
        else:
            self.joint = joint(r_p, r_b)
        self.h = h
        self.c_b = c_b
        self.c_p = c_p
        self.s_p = s_p
        self.salvage = salvage
        self.mode = mode
        # size of nested list that stores the calculated cost to go values:
        self.num_i = len(T)
        self.num_t = max(T) + 1
        max_n = sum(self.Q) + self.n_init
        if self.mode == 'standard':
            self.min_n = n_init - max(max(self.r_p[:, 0]), max(self.r_b[:, 0])) * sum(self.T)
            self.num_m = int(max(self.r_b[:, 0]) * sum(self.T) + 1)
        elif self.mode == 'joint':
            self.min_n = n_init - max(self.joint[:, 0] + self.joint[:, 1]) * sum(self.T)
            self.num_m = int(max(self.joint[:, 1]) * sum(self.T) + 1)
        else:
            raise ValueError('mode should be either standard or joint')
        self.num_n = max_n - self.min_n + 1
        self.num_m = int(max(self.r_b[:, 0]) * sum(self.T) + 1)
        self.memoized = [[[[None] * self.num_m for _ in range(self.num_n)] for _ in range(self.num_t)] for _ in range(self.num_i)] # nested list that stores the cost to go values
        self.memoized_decisions = [[[[None] * self.num_m for _ in range(self.num_n)] for _ in range(self.num_t)] for _ in range(self.num_i)] # nested list that stores the decisions (results of minimization problems in expectation2 and expectation_joint)
        if not (len(T) == len(Q) + 1):
            print('The length of Q should be one less than T')
            assert(len(T) == len(Q) + 1)

    def expectation_premium(self, i, t, n, m):
        '''Calculates the cost to go for the premium demand'''
        temp = np.array([self.V(i, t + 1, n - x, m) + self.h * max(0, n - x) + self.c_p * max(0, x - n) + self.c_b * m for x in self.r_p[:, 0]])
        # print('expectation1')
        # print(i,t,n,m)
        # print('temp: ', temp)
        # print(np.dot(temp, self.r_p[:, 1]))
        return np.dot(temp, self.r_p[:, 1])

    def expectation_base(self, i, t, n, m):
        '''Calculates the cost to go for the base demand'''
        temp = np.array([min(self.V(i, t+1, n, m + x) + self.h * max(0, n) + self.c_b * (m + x) + self.c_p * max(0, -n), \
            self.V(i, t+1, max(0, n - x) if n > 0 else n, m + (max(0, x - n) if n > 0 else x)) + self.h * max(0, n - x) + self.c_b * (m + (max(0, x - n) if n >= 0 else x)) + self.c_p * max(0, -n))  for x in self.r_b[:, 0]])
        fulfill_boolean = np.array([bool(np.argmin([self.V(i, t+1, n, m + x) + self.h * max(0, n) + self.c_b * (m + x) + self.c_p * max(0, -n), \
            self.V(i, t+1, max(0, n - x) if n > 0 else n, m + (max(0, x - n) if n > 0 else x)) + self.h * max(0, n - x) + self.c_b * (m + (max(0, x - n) if n >= 0 else x)) + self.c_p * max(0, -n)]))  for x in self.r_b[:, 0]])
        self.memoized_decisions[i][t][n - self.min_n][m] = fulfill_boolean
        # print('expectation2')
        # print(i,t,n,m)
        # print('temp: ', temp)
        # print(np.dot(temp, self.r_b[:, 1]))
        return np.dot(temp, self.r_b[:, 1])
    
    def expectation_joint(self, i, t, n, m):
        '''Calculates the cost to go using a joint distribution of premium and base demand'''
        fulfill_boolean = [bool(np.argmin([self.V(i, t + 1, n - x, m + y) + self.h * max(0, n - x) + self.c_p * max(0, x - n) + self.c_b * (m + y), \
            self.V(i, t + 1, max(0, n - x - y) if n - x > 0 else n - x, m + (max(0, y - (n - x)) if n - x > 0 else y)) \
                 + self.h * max(0, max(0, n - x - y) if n - x > 0 else n - x) + self.c_p * max(0, -(max(0, n - x - y) if n - x > 0 else n - x)) \
                      + self.c_b * (m + (max(0, y - (n - x)) if n - x >= 0 else y))])) for x, y  in self.joint[:, 0:2]]
        # this variable stores whether the base customer order's were fulfilled
        cost_to_go = np.array([min(self.V(i, t + 1, n - x, m + y) + self.h * max(0, n - x) + self.c_p * max(0, x - n) + self.c_b * (m + y), \
            self.V(i, t + 1, max(0, n - x - y) if n - x > 0 else n - x, m + (max(0, y - (n - x)) if n - x >= 0 else y)) \
                 + self.h * max(0, max(0, n - x - y) if n - x > 0 else n - x) + self.c_p * max(0, -(max(0, n - x - y) if n - x > 0 else n - x)) \
                      + self.c_b * (m + (max(0, y - (n - x)) if n - x >= 0 else y))) for x, y  in self.joint[:, 0:2]])
        # x is the premium demand, y is the base demand
        self.memoized_decisions[i][t][n - self.min_n][m] = fulfill_boolean
        # print('expectation_joint')
        # print(i,t,n,m)
        return np.dot(cost_to_go, self.joint[:, 2])

    def V(self, i=0, t=0, n=None, m=0, mode='standard'):
        '''Function that is called iteratively to calculate the cost-to-go. i is the period, t is the time step 
        within a period, n is the inventory level, m is the number of backloged low priority units and the mode allows to
        toggle between the standard dynamic programming algorithm which resemble the on in Chen (2014) and the "joint" algorithm
        is described in my master thesis and uses the joint distribution of the low and high priority classes'''
        if n is None:
            n = self.n_init
        assert(n - self.min_n >= 0)
        try:
            self.memoized[i][t][n - self.min_n][m]
        except:
            print(i,t,n,m)
        if self.memoized[i][t][n - self.min_n][m] is None:
            if t < self.T[i]:
                if self.mode == 'standard':
                    V_ = self.pi_0 * (self.V(i, t+1, n, m) + self.h * n + self.c_p * max(0, -n) + self.c_b * m) + \
                        self.pi_p * self.expectation_premium(i, t, n, m) + \
                        self.pi_b * self.expectation_base(i, t, n, m)
                else:
                    V_ = self.expectation_joint(i, t, n, m)
                # print(i, t, n, m)
                # print(V_)
            elif i == len(self.T) - 1: # last step of simulation, no replenishments arrive
                V_ = self.s_p * max(0, -n + m) + self.salvage * max(0, n - m)
                # print(i, t, n, m)
                # print(V_)
            else: # last step of period (t == self.T[i]), this is when the replenishment arrives, this is an articicial period between the end of a period and the beginning of the next
                V_ = self.V(i+1, 0, n + self.Q[i] if n + self.Q[i] <= 0 else max(0, n + self.Q[i] - m), m if n + self.Q[i] <= 0 else max(0,m - n - self.Q[i])) # fulfill all orders that can be fulfilled
                # print(i, t, n, m)
                # print(V_)
            self.memoized[i][t][n - self.min_n][m] = V_ # save the calculated cost-to-go
            return V_
        else:
            return self.memoized[i][t][n - self.min_n][m]

def joint(distribution1, distribution2):
    distribution1 = pd.DataFrame(distribution1, columns=['value_premium', 'proba_premium'])
    distribution2 = pd.DataFrame(distribution2, columns=['value_base', 'proba_base'])
    distribution1.loc[:, 'temp'] = 1
    distribution2.loc[:, 'temp'] = 1
    joint_distribution = pd.merge(distribution1, distribution2, how = 'outer')
    joint_distribution.loc[:, 'joint_proba'] = joint_distribution.proba_premium * joint_distribution.proba_base
    joint_distribution = joint_distribution[['value_premium', 'value_base', 'joint_proba']]
    return np.array(joint_distribution)

# # memoize stage by stage
# def V(i, t, n, m):
#     if memoized:
#         return memoized
#     else:
#         if t < T[i]:
#             V_i = pi_0 * (V(i, t+1, n, m) + h * n) + \
#                 pi_p * expectation1(i, t, n, m) + \
#                 pi_b * expectation2(i, t, n, m)
#         elif i == len(T) - 1:
#             V_i = s_p * max(0, -n) + salvage * max(0, n)
#         else:
#             V_i = V(i+1, 0, max(0, n + Q[i] - m), max(0, -n - Q[i] + m))
#         memoize
#     return V_i

# def V(i, t, n, m):
#     if t < T:
#         V_i = pi_0 * (V(i, t+1, n, m) + h * n) + \
#             pi_p * expectation(V(i, t+1, n - r_p, m) + h * max(0, n - r_p) + c_p * max(0, r_p - n) * (T[i] - t)) + \
#             pi_b * expectation(min(V(i, t+1, n, m + r_b) + h * n + c_b * r_b * (T[i] - t),    V(i, t+1, max(0, n - r_b), m + max(0, r_b - n) ) + h * max(0, n - r_b) * (T[i] - t)))
#     elif i == len(T):
#         V_i = s_p * max(0, -n) + salvage * max(0, n)
#     else:
#         V_i = V(i+1, 1, max(0, n + Q[i] - m), max(0, -n - Q[i] + m))
#     return V_i
    
