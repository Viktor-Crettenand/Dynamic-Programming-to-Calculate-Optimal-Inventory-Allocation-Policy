# Using-Dynamic-Programming-to-Calculate-Optimal-Inventory-Allocation-Policy

## Introduction
SAP’s aATP framework has one big flaw. It can not ration inventory automatically. The only
thing it allows for is to manually set consumption limits on customers or on priority classes.
Healthcare equipment companies typically have tens of thousands of SKUs which makes a manual
rationing of inventory practically impossible. Even if inventory could be rationned manually, it is hard to develop an intuition about how
much to ration in specific situations. Using judgement might lead to sub-optimal, or worse,
counter-productive rationing strategies.

In the code in this repository the approach followed by Wang et al. [2014] is extended to a general random
demand. Like in Wang et al. [2014], a supplier rationing inventory between two customer
classes is considered with holding costs and penalties for late inventory allocation. At the end
of each replenishment cycle, all backlogged demand is fulfilled within the limits of available
inventory. The model solved in this work differs from the one solved by Wang et al. [2014] in
three ways. The first, demand is described by a general probability distribution in this model
whereas in Wang et al. [2014], at most one unit is ordered in every time subdivision. The second
difference is that the penalties are not one-off penalties but have to be paid every day until the
order is fulfilled. The third difference is that Wang et al. [2014] considered a inventory model
with one period lead time for replenishment whereas this model assumes the replenishment
to be known in advance. This assumption was made because at BD, the out-of-control period
(period in which replenishment order can not be modified) is 1-3 months long, which for
many SKUs, is multiple replenishment cycles. The rationing will be performed on the horizon
of the out-of-control period.
At each time step the demand must be fulfilled immediately. The premium demand is fulfilled
first and in the limits of available inventory. Then the decision is taken whether to fulfill
the base demand of backlogging it. If it is decided to fulfill the base demand, it is fulfilled
in full or as much of it as can be given the inventory level. On the last time step of each
replenishment period, a replenishment is received and all backlogged units are fulfilled in 
the limits of available inventory starting with premium orders. At the end of the last period
considered, no replenishment is received. The left over units are sold at a salvage cost and a
penalty must be paid for each outstanding order.

## Method

In order to solve this model, it is formulated as a dynamic program. The dynamic programming
equations allows to calculate the cost-to-go function Vi (t , n, m) which is the expectation of
the holding cost and penalties to be payed until the end of the last period. The expectation
is calculated over the possible realization of the random demand which is given by the joint
probability distributions of the random variables rp and rb denoted r . i = 1 , ..., I runs over
the I replenishment periods considered, t = 1 , ..., Ti runs over the sub-intervals which were
chosen to be days, Ti is the number of days in the i th replenishment period, n is the stock level
if it is positive, and the number of outstanding units ordered by premium class customers and
m is the number of outstanding units ordered by base customers.
The cost-to-go is calculated by using the following recursive functions:

![image](https://user-images.githubusercontent.com/56121696/161269006-0dea4bfb-7e73-4f91-a402-6555eb42bda9.png)

where E{(rp ,rb )∼r } denotes the expectation over the joint distribution r of the random demands
rp and rb , h is the daily holding cost and cp and cb are the penalties per unit of inventory and
per day of delay for premium class and base class respectively. ˆn, ˆm, n? and m? are define by:

![image](https://user-images.githubusercontent.com/56121696/161269082-ed117cfa-2650-44a2-a25a-cde84e959848.png)

The equation to calculate the cost-to-go on the last day of each replenishment period, is the following:

![image](https://user-images.githubusercontent.com/56121696/161269218-b05e9c32-0925-4efd-a749-e291082600de.png)

where Qi is the replenishment quantity arriving at the end of period i .
The equation to calculate the cost-to-go on the last day of the last replenishment period, is the
following:

![image](https://user-images.githubusercontent.com/56121696/161269308-9b45b68e-7599-43a9-b3c9-a10f0b691af4.png)

where ps is the penalty for not having delivered a unit at the end of the last period and s is the
salvage value per unit.
The optimal rationing policy will be compared against a myopic prioritization policy which
serves premium customers first and base customers second as long as there is inventory. This
policy never backlogs base orders.

The file dynamic_programming.ipynb contains tests to make sure the model behaves as desired and to detect errors in the code as well as the comparison of the dynamic programming rationing policy with the myopic allocation policy.
The file dynamic_programming_helpers.py contains all the functions used for dynamic programming.

