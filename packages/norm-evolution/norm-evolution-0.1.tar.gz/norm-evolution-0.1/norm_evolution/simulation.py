#!/usr/bin/env python
# coding: utf-8

# In[9]:


import numpy as np   
import pandas as pd
from collections import Counter
import datetime
import random



# 1. seed : random seed. Integer
# 2. num_agents : number of agents. Integer
# 3. radius : agents neighbourhood size. E.g. if its value is set to 1 then each agent will look for 1 agent towards the left and 1 towards the right. Integer 
# 4. iteration_name: give any name for this iterations. String
# 5. num_strategy : total number of strategies. Integer
# 6. num_initial_possibilities: Number of possibilities to consider. This implies the distinct strategy distribution among agents with which the game is started.Integer.
# 7. time_period. how long the game should run. Integer
# 8. percent_share. percent distribution of strategies among agents. Must be specified in list. E.g.[0.4,0.4,0.2]. Must add up to 1. Specify in the order of strategies 0,1,2, and so on.	
# 9. strategy_pair. Strategy pair in dictionary format.E.g. {0: "H",1: "M",2: "L"}. 0 strategy is 'H', 1 strategy is 'M', and so on. Count must match with num_strategy argument. Keys would need to be 0,1,2, etc. Value corresponding to keys can be anything in string format.
#10. payoff_values. List of payoff values. E.g. [[0,0,70],[0,50,50],[30,30,30]]. the first list [0,0,70] is the first row of the 3*3 payoff matrix assuming we have 3 strategies. Second list [0,50,50] is the second row of the payoff matrix and third list [30,30,30] is the third row of payoff matrix.
## It looks something like below.
#	     [0,  0, 70
#         0, 50, 50
#        30, 30, 30]
# 11.path_to_save_output. the location where output excel files should be saved.



def simulation_function_neighbors(seed,
                                  num_agents,
                                  radius,
                                  iteration_name,
                                  num_strategy,
                                  num_initial_possibilities,
                                  time_period,
                                  percent_share,
                                  strategy_pair,
                                  payoff_values,
                                  path_to_save_output
                                 ):
 
								 
    
    SEED = seed
    NUM_AGENTS = num_agents
    RADIUS = radius
    IterationName = iteration_name
    NUM_STRATEGIES = num_strategy
    NUMBER_INITIAL_POSSIBILITIES = num_initial_possibilities
    TIME_PERIOD = time_period
    SHARE = percent_share
    thisdict = strategy_pair
    random.seed(SEED)
    payoff_matrix = np.zeros((NUM_STRATEGIES,NUM_STRATEGIES))
    for i in range(len(payoff_values)):
        payoff_matrix[i,]= payoff_values[i]
        
    today = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    
    list_to_fill = []
    for i in range(NUM_STRATEGIES):
        list_to_fill.append([i]*round(SHARE[i]*NUM_AGENTS))

    flat_list = [item for sublist in list_to_fill for item in sublist]

    if len(flat_list) == NUM_AGENTS:
        pass
#         print("ok")
    elif len(flat_list) < NUM_AGENTS:
        delta = NUM_AGENTS - len(flat_list)
        for kk in range(delta):
            flat_list.append(flat_list[-1])
#         print("last elements added")
    else:
        delta = len(flat_list) - NUM_AGENTS
        for kk in range(delta):
            flat_list.pop()
#         print("last elements deleted")

    sample_initial_possibilities = []
    for ll in range(NUMBER_INITIAL_POSSIBILITIES):
        sample_initial_possibilities.append(random.sample(flat_list,len(flat_list)))

    trend_db_to_store = pd.DataFrame(columns=["count","strategy","percent_count","timeperiod_number","starting_position"])
    for pp in range(len(sample_initial_possibilities)):
        samplelist1 = sample_initial_possibilities[pp]
        for timeperiod in range(TIME_PERIOD):
            final_strategy_to_fill = []
            Payoffs_to_fill = []
            for i in range(len(samplelist1)):

                left_side = []
                for kk in range(RADIUS):
                    left_side.append(payoff_matrix[samplelist1[i],samplelist1[i-kk-1]])

                right_side = []
                for kk in range(RADIUS):
                    try:
                        right_side.append(payoff_matrix[samplelist1[i],samplelist1[i+kk+1]])
                    except:
                        right_side.append(payoff_matrix[samplelist1[i],samplelist1[kk]])


                Payoffs_to_fill.append(sum(left_side)+sum(right_side))

            foopd = pd.DataFrame([Payoffs_to_fill,samplelist1]).T 
            foopd.columns = ['payoff','strategy']

            for i in range(len(foopd)):

                left_side_payoff = []
                left_side_strategy = []
                for kk in range(RADIUS):
                    left_side_payoff.append(foopd.iloc[i-kk-1]['payoff'])
                    left_side_strategy.append(foopd.iloc[i-kk-1]['strategy'])

                maxIndexList = [index for index,value in enumerate(left_side_payoff) if value==max(left_side_payoff)]
                payoff_1_left = []
                for jj in range(len(maxIndexList)):
                    payoff_1_left.append(left_side[maxIndexList[jj]])

                compare_left = [k for k in payoff_1_left if k > foopd.iloc[i]['payoff']]
                left_strategy_to_fill = []
                if len(compare_left) == 0:
#                     print("fill the existing strategy")
                    left_strategy_to_fill.append(foopd.iloc[i]['strategy'])

                elif len(compare_left) == 1:
                    left_strategy_to_fill.append(left_side_strategy[maxIndexList[0]])
                else:
#                     print("select random strategy")
                    left_strategy_to_fill.append(left_side_strategy[random.sample(maxIndexList,1)[0]])


                ###### Right strategy


                right_side_payoff = []
                right_side_strategy = []
                for kk in range(RADIUS):
                    try:

                        right_side_payoff.append(foopd.iloc[i+kk+1]['payoff'])
                        right_side_strategy.append(foopd.iloc[i+kk+1]['strategy'])

                    except:

                        right_side_payoff.append(foopd.iloc[kk]['payoff'])
                        right_side_strategy.append(foopd.iloc[kk]['strategy'])


                maxIndexList = [index for index,value in enumerate(right_side_payoff) if value==max(right_side_payoff)]
                payoff_1_right = []
                for jj in range(len(maxIndexList)):
                    payoff_1_right.append(right_side_payoff[maxIndexList[jj]])

                compare_right = [k for k in payoff_1_right if k > foopd.iloc[i]['payoff']]
                right_strategy_to_fill = []
                if len(compare_right) == 0:
                   # print("fill the existing strategy")
                    right_strategy_to_fill.append(foopd.iloc[i]['strategy'])

                elif len(compare_right) == 1:
                    right_strategy_to_fill.append(right_side_strategy[maxIndexList[0]])
                else:
                   # print("select random strategy")
                    right_strategy_to_fill.append(right_side_strategy[random.sample(maxIndexList,1)[0]])


                ##### compare left and right payoffs


                if left_strategy_to_fill == right_strategy_to_fill:
                    #### can append anaything as both are same...
#                     print(str(i) +"_fillled existing")

                    final_strategy_to_fill.append(right_strategy_to_fill[0])
                else:

                    if len(compare_left) != 0 and len(compare_right) !=0 :
                        left_is_higher = [x for x,y in zip(compare_left,compare_right) if x > y ]
                        right_is_higher = [x for x,y in zip(compare_right,compare_left) if x > y ]

                        if len(left_is_higher) > 0:
#                             print(str(i) +"_fillled left")
                            final_strategy_to_fill.append(left_strategy_to_fill[0])

                        if len(right_is_higher) > 0:
#                             print(str(i) +"_fillled right")
                            final_strategy_to_fill.append(right_strategy_to_fill[0])


                        if len(left_is_higher) == 0 and len(right_is_higher) == 0:
                        #### case where both left and right side has equal payoffss
#                             print(str(i) +"_seleted randomly")
                            left_strategy_to_fill.append(right_strategy_to_fill[0])

                            final_strategy_to_fill.append(random.sample(left_strategy_to_fill,1)[0])


                    if len(compare_left) == 0 and len(compare_right) !=0:
#                         print(str(i) +"_fillled right2")
                        final_strategy_to_fill.append(right_strategy_to_fill[0])


                    if len(compare_left) != 0 and len(compare_right) ==0:
#                         print(str(i) +"_fillled left2")
                        final_strategy_to_fill.append(left_strategy_to_fill[0])



#             d = {x:final_strategy_to_fill.count(x) for x in final_strategy_to_fill}
            cc = Counter(final_strategy_to_fill)
            d=dict(cc)
            foo_last = pd.DataFrame([d],columns=d.keys()).T
            foo_last.columns = ["count"]
            foo_last = foo_last.sort_values(by="count",ascending=False)
            foo_last["strategy"] = foo_last.index.tolist()
            foo_last["percent_count"] = foo_last["count"]/sum(foo_last["count"])
            foo_last["percent_count"] = round(foo_last["percent_count"]*100,2)
            foo_last["timeperiod_number"] = timeperiod
            foo_last["starting_position"] = str([thisdict[k] for k in sample_initial_possibilities[pp]]) 
            trend_db_to_store = trend_db_to_store.append(foo_last,ignore_index=True)

    trend_db_to_store = trend_db_to_store.replace({"strategy":thisdict})
    trend_db_to_store["iteration_name"] = IterationName
    trend_db_to_store["num_strategy"] = NUM_STRATEGIES
    trend_db_to_store["time_period"] = TIME_PERIOD
    trend_db_to_store["num_agents"] = NUM_AGENTS
    trend_db_to_store["radius"] = RADIUS
    trend_db_to_store["num_initial_possibilities"] = NUMBER_INITIAL_POSSIBILITIES
    trend_db_to_store["percent_share"] = str(SHARE)
    trend_db_to_store["strategy_pair"] = str(thisdict)
    trend_db_to_store["random_seed"] = SEED
   



    trend_db_to_store.to_excel(path_to_save_output+"timperiod_data_"+iteration_name+"_"+today+".xlsx",index=None)

    d = {x:sample_initial_possibilities[pp].count(x) for x in sample_initial_possibilities[pp]}        
    foo_last = pd.DataFrame([d],columns=d.keys()).T
    foo_last.columns = ["count"]
    foo_last = foo_last.sort_values(by="count",ascending=False)
    foo_last["strategy"] = foo_last.index.tolist()
    foo_last["percent_count"] = foo_last["count"]/sum(foo_last["count"])
    foo_last["percent_count"] = round(foo_last["percent_count"]*100,2)
    foo_last = foo_last.replace({"strategy":thisdict})

    foo_last["iteration_name"] = IterationName
    foo_last["num_strategy"] = NUM_STRATEGIES
    foo_last["time_period"] = TIME_PERIOD
    foo_last["num_agents"] = NUM_AGENTS
    foo_last["radius"] = RADIUS
    foo_last["num_initial_possibilities"] = NUMBER_INITIAL_POSSIBILITIES
    foo_last["percent_share"] = str(SHARE)
    foo_last["strategy_pair"] = str(thisdict)
    foo_last["random_seed"] = SEED

    foo_last.to_excel(path_to_save_output+"OriginalPercentdistribution_data_"+iteration_name+"_"+today+".xlsx",index=None)

    return(print("done"))