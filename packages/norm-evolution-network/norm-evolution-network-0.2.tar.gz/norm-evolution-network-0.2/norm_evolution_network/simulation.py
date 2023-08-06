#!/usr/bin/env python
# coding: utf-8

# In[9]:


import numpy as np   
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import datetime
import random
import string



# 1. num_neighbors: number of neighbours. Integer
# 2. num_agents: number of agents. Integer
# 3. prob_edge_rewire: small world network parameter. Probability of rewiring each edge. Float
# 4. grid_network_m:  2-dimensional grid network parameter. Number of nodes. Integer
# 5. grid_network_n:  2-dimensional grid network parameter. Number of nodes. Integer
# 6. name_len: length of random keywords created by the game. Integer
# 7. num_of_rounds: number of rounds. Integer
# 8. num_of_trials: number of trials. Integer    
# 9. fixed_agents_ratio: percentage of agents assumed as fixed. Float
# 10. perturb_ratio: probability of agents taking action randomly. Float
# 11. cutoff_norms:  minimum threshold for norm emergence. A number between 1 and 100. E.g. 50 means the specific norm has been played at least 50% of times. Integer 
# 12. network_name: specify one of these values [small_world1,small_world2,small_world3,complete,random,grid2d]. String
# 13. random_seed: random seed value. Integer 
# 14. function_to_use: specify one of these values [perturbed_response1,perturbed_response2,perturbed_response3,perturbed_response4]. String  
# 15. iteration_name: iteration name. String
# 16. path_to_save_output: path to save output files. String   

# function_to_use
# perturbed_response1: Agent selects the best response (1-perturb_ratio)*100% times among the strategies which are most frequently used. Agents selects random strategy (perturb_ratio)*100% times from which are not most frequently used.
# perturbed_response2: Agent selects strategy according to the % share in which it has been used by opponents in the past.
# perturbed_response3: This is same as perturbed_response1 function except agent selects random strategy (perturb_ratio)*100% times from all the strategies. 
# perturbed_response4: Agent selects the best response 100% times among the strategies which are most frequently used. There is no perturbation element.
    
 
# Note there may be instances wherein more than 1 strategy has been used by opponent agents more frequently.
# E.g. if an agent comes across s1 and s2 strategy used by their opponent agents most frequently during any history and both s1 and s2
# have been used equally in the past, in that case agent deciding to take action will select randomly from s1 and s2.


# network_name
# small_world1: Returns a Watts–Strogatz small-world graph. Here number of edges remained constant once we increase the prob_edge_rewire value.Shortcut edges if added would replace the existing ones. But total count of edges remained constant.
# small_world2: Returns a Newman–Watts–Strogatz small-world graph. Here number of edges increased once we increase the prob_edge_rewire value. Would add more shortcut edges in addition to what already exist.
# small_world3: Returns a connected Watts–Strogatz small-world graph.
# complete: Returns the complete graph.
# random: Compute a random graph by swapping edges of a given graph.
# grid2d: Return the 2d grid graph of mxn nodes, each connected to its nearest neighbors.



def perturbed_response1(AGENT_NO,data_to_look,perturb_ratio,name_len):
    try:
        count_pd = data_to_look.loc[data_to_look["agent"]==AGENT_NO]["name_offered_by_opponent"].value_counts().reset_index()
        count_pd["tot_sum"] = count_pd["name_offered_by_opponent"] / sum(count_pd["name_offered_by_opponent"])
        best_response = count_pd.loc[count_pd["tot_sum"] == max(count_pd["tot_sum"])]['index'].tolist()
        draw1= random.choices(population=best_response,k=1)
        
        Nonbest_response = count_pd.loc[count_pd["tot_sum"] != max(count_pd["tot_sum"])]['index'].tolist()
        if len(Nonbest_response) > 0:
            draw2= random.choices(population=Nonbest_response,k=1)
            best_response = random.choices(population=[draw1[0],draw2[0]],weights=[1-perturb_ratio,perturb_ratio],k=1)
            best_response = best_response[0]
        else:
            best_response = draw1[0]
        
        
    except:
        best_response = [''.join(random.choices(string.ascii_uppercase+string.digits,k=name_len))]
        best_response = best_response[0]
        
    return best_response



def perturbed_response2(AGENT_NO,data_to_look,name_len):
    try:
        count_pd = data_to_look.loc[data_to_look["agent"]==AGENT_NO]["name_offered_by_opponent"].value_counts().reset_index()
        count_pd["tot_sum"] = count_pd["name_offered_by_opponent"] / sum(count_pd["name_offered_by_opponent"])
        names_list = count_pd['index'].tolist()
        share_list = count_pd['tot_sum'].tolist()
        draw1= random.choices(population=names_list,weights=share_list,k=1)
        best_response = draw1[0]
        
        
    except:
        best_response = [''.join(random.choices(string.ascii_uppercase+string.digits,k=name_len))]
        best_response = best_response[0]
        
    return best_response



def perturbed_response3(AGENT_NO,data_to_look,perturb_ratio,name_len):
    try:
        count_pd = data_to_look.loc[data_to_look["agent"]==AGENT_NO]["name_offered_by_opponent"].value_counts().reset_index()
        count_pd["tot_sum"] = count_pd["name_offered_by_opponent"] / sum(count_pd["name_offered_by_opponent"])
        best_response = count_pd.loc[count_pd["tot_sum"] == max(count_pd["tot_sum"])]['index'].tolist()
        draw1= random.choices(population=best_response,k=1)
        
        Nonbest_response = count_pd['index'].tolist()
        draw2= random.choices(population=Nonbest_response,k=1)
        best_response = random.choices(population=[draw1[0],draw2[0]],weights=[1-perturb_ratio,perturb_ratio],k=1)
        best_response = best_response[0]
        
    except:
        best_response = [''.join(random.choices(string.ascii_uppercase+string.digits,k=name_len))]
        best_response = best_response[0]
        
    return best_response



def perturbed_response4(AGENT_NO,data_to_look,name_len):
    try:
        count_pd = data_to_look.loc[data_to_look["agent"]==AGENT_NO]["name_offered_by_opponent"].value_counts().reset_index()
        count_pd["tot_sum"] = count_pd["name_offered_by_opponent"] / sum(count_pd["name_offered_by_opponent"])
        best_response = count_pd.loc[count_pd["tot_sum"] == max(count_pd["tot_sum"])]['index'].tolist()
        draw1= random.choices(population=best_response,k=1)
        best_response = draw1[0]
        
    except:
        best_response = [''.join(random.choices(string.ascii_uppercase+string.digits,k=name_len))]
        best_response = best_response[0]
        
    return best_response
	

def network_simulations(num_neighbors,
                        num_agents,
                        prob_edge_rewire,
                        grid_network_m,
                        grid_network_n,
                        name_len,
                        num_of_rounds,
                        num_of_trials,
                        fixed_agents_ratio,
                        perturb_ratio,
                        cutoff_norms,
                        network_name,
                        random_seed,
                        function_to_use,         
                        iteration_name,
                        path_to_save_output
                        ):
    
    
    iteration_name = iteration_name
    path_to_save_output = path_to_save_output
    today = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    num_neighbors = num_neighbors
    num_agents= num_agents
    prob_edge_rewire = prob_edge_rewire
    grid_network_m=grid_network_m
    grid_network_n=grid_network_n
    name_len = name_len
    num_of_rounds = num_of_rounds
    num_of_trials = num_of_trials
    fixed_agents_ratio = fixed_agents_ratio
    perturb_ratio = perturb_ratio
    cutoff_norms = cutoff_norms
    network_name = network_name
    random_seed = random_seed
    function_to_use = function_to_use
    random.seed(random_seed)
    
    
    if network_name == 'small_world1': 
        G = nx.watts_strogatz_graph(num_agents,num_neighbors,prob_edge_rewire)
    if network_name == 'small_world2': 
        G = nx.newman_watts_strogatz_graph(n=num_agents,k=num_neighbors,p=prob_edge_rewire,seed=random_seed)
    if network_name == 'small_world3':
        G = nx.connected_watts_strogatz_graph(n=num_agents,k=num_neighbors,p=prob_edge_rewire,seed=random_seed)
    if network_name == 'complete':
        G = nx.complete_graph(num_agents)
    if network_name == 'random':
        G = nx.watts_strogatz_graph(num_agents,num_neighbors,prob_edge_rewire)
        G = nx.random_reference(G, niter=5, connectivity=True, seed=random_seed)
    if network_name == 'grid2d':
        G = nx.grid_2d_graph(m=grid_network_m,n=grid_network_n)
        mapping = dict(zip(G, range(len(G))))
        G = nx.relabel_nodes(G, mapping)
    
    
    
    
    potential_edges = list(G.edges)
    vcheck = random.sample(potential_edges,1)
    NUM_SUBJECTS = len(G)
    TOT_NO_PAIRS = int(NUM_SUBJECTS/2)


    PAIRS_TO_FILL = []
    AGENTS_ALREADY_CAME = []
    PAIRS_TO_FILL.append(vcheck[0])
    AGENTS_ALREADY_CAME.append(vcheck[0][0])
    AGENTS_ALREADY_CAME.append(vcheck[0][1])

    delta_agents = [i for i in list(range(NUM_SUBJECTS)) if i not in AGENTS_ALREADY_CAME]

    empty_df_to_fill = pd.DataFrame()

    empty_df_to_fill["agent"] = -1
    empty_df_to_fill["name_offered"] = ''
    empty_df_to_fill["opponentagent"] = -1
    empty_df_to_fill["name_offered_by_opponent"] = ''
    empty_df_to_fill["round"] = -1
    empty_df_to_fill["pair"] = ""
    empty_df_to_fill["trial"] = -1

    random_name = ''.join(random.choices(string.ascii_uppercase+string.digits,k=name_len))

    for v in range(len(PAIRS_TO_FILL)):
        vcheck = PAIRS_TO_FILL[v]
        agent1 = vcheck[0]
        agent2 = vcheck[1]

        random_name1 = ''.join(random.choices(string.ascii_uppercase+string.digits,k=name_len))
        random_name2 = ''.join(random.choices(string.ascii_uppercase+string.digits,k=name_len))
        empty_df_to_fill = pd.concat([empty_df_to_fill,pd.DataFrame([{'agent':agent1,'name_offered':random_name1,'opponentagent':agent2,'name_offered_by_opponent':random_name2,'round':-1,'pair':str(vcheck),'trial':-1}])],ignore_index=True,sort=False)

    opponent_db = empty_df_to_fill[["opponentagent","name_offered_by_opponent","name_offered","agent","pair","round","trial"]]
    opponent_db.columns = ["agent","name_offered","name_offered_by_opponent","opponentagent","pair","round","trial"]
    empty_df_to_fill = pd.concat([empty_df_to_fill,opponent_db],ignore_index=True,sort=False)

    empty_df_to_fill_trial = empty_df_to_fill.copy()
    Fixed_agents_ratio = round(fixed_agents_ratio*len(G)) #no of agents parameter #

    fixed_agents = random.sample(population=list(range(len(G))),k=Fixed_agents_ratio)
    fixed_list =empty_df_to_fill.loc[empty_df_to_fill["agent"].isin(fixed_agents)][["agent","name_offered"]].reset_index(drop=True)
    if len(fixed_list) > 0:
        fixed_list=fixed_list.drop_duplicates()
        fixed_values_to_use = dict(zip(fixed_list.agent,fixed_list.name_offered))
    else:
        fixed_values_to_use = dict()

    for u in range(1,num_of_trials+1):
        for v in range(1,num_of_rounds+1):
            vcheck = random.sample(potential_edges,1)
            agent1 = vcheck[0][0]
            agent2 = vcheck[0][1]

            if function_to_use == 'perturbed_response1':
                name_to_fill1 = perturbed_response1(AGENT_NO = agent1,data_to_look = empty_df_to_fill_trial,perturb_ratio=perturb_ratio,name_len=name_len)
                name_to_fill2 = perturbed_response1(AGENT_NO = agent2,data_to_look = empty_df_to_fill_trial,perturb_ratio=perturb_ratio,name_len=name_len)
            elif function_to_use == 'perturbed_response2':
                name_to_fill1 = perturbed_response2(AGENT_NO = agent1,data_to_look = empty_df_to_fill_trial,name_len=name_len)
                name_to_fill2 = perturbed_response2(AGENT_NO = agent2,data_to_look = empty_df_to_fill_trial,name_len=name_len)
            elif function_to_use == 'perturbed_response3':
                name_to_fill1 = perturbed_response3(AGENT_NO = agent1,data_to_look = empty_df_to_fill_trial,perturb_ratio=perturb_ratio,name_len=name_len)
                name_to_fill2 = perturbed_response3(AGENT_NO = agent2,data_to_look = empty_df_to_fill_trial,perturb_ratio=perturb_ratio,name_len=name_len)
            elif function_to_use == 'perturbed_response4':
                name_to_fill1 = perturbed_response4(AGENT_NO = agent1,data_to_look = empty_df_to_fill_trial,name_len=name_len)
                name_to_fill2 = perturbed_response4(AGENT_NO = agent2,data_to_look = empty_df_to_fill_trial,name_len=name_len)



            if agent1 in fixed_agents:
                try:
                    name_offered = fixed_values_to_use[agent1]
                except:
                    name_offered = name_to_fill1
            else:
                name_offered = name_to_fill1


            if agent2 in fixed_agents:
                try:
                    name_offered_by_opponent = fixed_values_to_use[agent2]
                except:
                    name_offered_by_opponent = name_to_fill2
            else:
                name_offered_by_opponent = name_to_fill2


            data_to_append = pd.DataFrame({'agent':agent1,
                                               'name_offered':name_offered,
                                               'name_offered_by_opponent':name_offered_by_opponent,
                                               'opponentagent':agent2,
                                               'pair':str(vcheck[0]), 
                                               'round':v,
                                               'trial':u},index=[0])

            data_to_append2 = pd.DataFrame({'agent':agent2,
                                               'name_offered':name_offered_by_opponent,
                                               'name_offered_by_opponent':name_offered,
                                               'opponentagent':agent1,
                                               'pair':str(vcheck[0]), 
                                               'round':v,
                                               'trial':u},index=[0])    

            empty_df_to_fill_trial = pd.concat([empty_df_to_fill_trial,data_to_append,data_to_append2],ignore_index=True,sort=False)

            if len(fixed_values_to_use) < len(fixed_agents):
                for jj in fixed_agents:
                    if jj not in list(fixed_values_to_use.keys()):
                        xx = empty_df_to_fill_trial.loc[empty_df_to_fill_trial["agent"]==jj].sort_values(["trial","round"],ascending=[True,True]).head(1)
                        if len(xx) > 0:
                            fixed_values_to_use[xx["agent"].values[0]]=xx["name_offered"].values[0]


    list_to_fill_for_labels = []
    for i in range(len(G)):
        perct_share = empty_df_to_fill_trial.loc[empty_df_to_fill_trial["agent"]==i]["name_offered"].value_counts(normalize=True).to_frame()
        perct_share["name_index"] = perct_share.index.tolist()
        xx = str(i)+ '-' +perct_share.head(1)["name_index"][0] +'-' + str(int(perct_share.head(1)["name_offered"][0]*100)) + '%'
        list_to_fill_for_labels.append(xx)


    list_to_fill_for_labels_2 = []
    for i in range(len(G)):
        perct_share = empty_df_to_fill_trial.loc[empty_df_to_fill_trial["agent"]==i]["name_offered"].value_counts(normalize=True).to_frame()
        perct_share["name_index"] = perct_share.index.tolist()
        xx = perct_share.head(1)["name_index"][0]
        list_to_fill_for_labels_2.append(xx)


    with open(path_to_save_output+"agent_mostfrequent_percentshare_"+iteration_name+"_"+today+".txt",'w') as f:
        for item in list_to_fill_for_labels:
            f.write("%s\n" % item)
        
    names_to_check = list(np.unique(list_to_fill_for_labels_2))
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF),range(n)))
    list_of_colors = get_colors(len(names_to_check))
    color_map = []
    for j in range(len(list_to_fill_for_labels_2)):
        for i in range(len(names_to_check)):
            if list_to_fill_for_labels_2[j] == names_to_check[i]:
                color_map.append(list_of_colors[i])

    for i in range(len(G)):
        G.nodes[i]["name_offered"] = list_to_fill_for_labels[i]


    labels_for_graph = nx.get_node_attributes(G,"name_offered")
    nx.draw(G,node_color=color_map,with_labels=True)
    l,r = plt.xlim()
    plt.xlim(l-0.05,r+0.05)
    plt.savefig(path_to_save_output+"normsgraph_"+iteration_name+"_"+today+".png")


    
    empty_df_to_fill_trial = empty_df_to_fill_trial.sort_values(["trial","round"])
    agent_no_to_fill = []
    for j in names_to_check:
        xx = empty_df_to_fill_trial.loc[empty_df_to_fill_trial["name_offered"]==j].head(1)["agent"].values[0]
        agent_no_to_fill.append(xx)

    data1_to_save = pd.DataFrame({'first_agent_propose_the_name':agent_no_to_fill,'name_proposed':names_to_check})
    data1_to_save.to_excel(path_to_save_output+"firstagent_"+iteration_name+"_"+today+".xlsx",index=None)

    data2_to_save = empty_df_to_fill_trial["pair"].value_counts(normalize=True).to_frame()
    data2_to_save.columns=["percent_share"]
    data2_to_save["pair"]=data2_to_save.index.values

    data2_to_save.to_excel(path_to_save_output+"agent_pairs_distribution_"+iteration_name+"_"+today+".xlsx",index=None)

    data3_to_save = empty_df_to_fill_trial["agent"].value_counts(normalize=True).to_frame()
    data3_to_save.columns=["percent_share"]
    data3_to_save["agent"]=data3_to_save.index.values

    data3_to_save.to_excel(path_to_save_output+"agent_distribution_"+iteration_name+"_"+today+".xlsx",index=None)

    data4_to_save = empty_df_to_fill_trial["opponentagent"].value_counts(normalize=True).to_frame()
    data4_to_save.columns=["percent_share"]
    data4_to_save["opponentagent"]=data4_to_save.index.values

    data4_to_save.to_excel(path_to_save_output+"opponentagent_distribution_"+iteration_name+"_"+today+".xlsx",index=None)


    empty_df_to_fill_trial = empty_df_to_fill_trial.sort_values(['trial','round'],ascending=True)
    db_to_fill = pd.DataFrame()
    db_to_fill["agent"] = -1
    db_to_fill["round"] = -1
    db_to_fill["trial"] = -1
    db_to_fill["name_offered"] = -1


    
    for j in range(len(G)):
        foocheck = empty_df_to_fill_trial.loc[empty_df_to_fill_trial["agent"]==j]
        for i in names_to_check:
            foocheck["count_names_offered"] = (foocheck["name_offered"]==i).cumsum()
            foocheck["cum_perc"] = 100*foocheck["count_names_offered"]/foocheck.shape[0]
            xxxx= foocheck.loc[foocheck["cum_perc"]>=cutoff_norms][["round","trial"]].head(1)
            if xxxx.shape[0]>0:
                roundv = foocheck.loc[foocheck["cum_perc"]>=cutoff_norms][["round","trial"]].head(1)["round"].values[0]
                trialv = foocheck.loc[foocheck["cum_perc"]>=cutoff_norms][["round","trial"]].head(1)["trial"].values[0]
                foodb = pd.DataFrame({"agent":[j],"round":[roundv],"trial":[trialv],"name_offered":[i]})
                db_to_fill = pd.concat([db_to_fill,foodb],ignore_index=True,sort=False)

    if len(db_to_fill)>0:
        db_to_fill = db_to_fill.sort_values(["name_offered","trial","round"])
        db_to_fill.to_excel(path_to_save_output+"agent_norm_trail_round_"+iteration_name+"_"+today+".xlsx",index=None)

    db_to_fill2 = pd.DataFrame()
    db_to_fill2["round"] = -1
    db_to_fill2["trial"] = -1
    db_to_fill2["name_offered"] = -1

    for j in names_to_check:
        foocheck = empty_df_to_fill_trial.loc[empty_df_to_fill_trial["name_offered"]==j]
        foocheck = foocheck.sort_values(["trial","round"])
        foocheck["count_names_offered"] = (foocheck["name_offered"]==j).cumsum()
        foocheck["cum_perc"] = 100*foocheck["count_names_offered"]/foocheck.shape[0]
        xxxx= foocheck.loc[foocheck["cum_perc"]>=cutoff_norms][["round","trial"]].head(1)
        if xxxx.shape[0]>0:
            roundv = foocheck.loc[foocheck["cum_perc"]>=cutoff_norms][["round","trial"]].head(1)["round"].values[0]
            trialv = foocheck.loc[foocheck["cum_perc"]>=cutoff_norms][["round","trial"]].head(1)["trial"].values[0]
            foodb = pd.DataFrame({"round":[roundv],"trial":[trialv],"name_offered":[j]})
            db_to_fill2 = pd.concat([db_to_fill2,foodb],ignore_index=True,sort=False)

    if len(db_to_fill2) > 0:
        db_to_fill2 = db_to_fill2.sort_values(["trial","round"])
        db_to_fill2 = db_to_fill2[["name_offered","trial","round"]]
        db_to_fill2.to_excel(path_to_save_output+"aggregate_norm_trail_round_"+iteration_name+"_"+today+".xlsx",index=None)

    empty_df_to_fill_trial.to_excel(path_to_save_output+"aggregate_data_detailed_"+iteration_name+"_"+today+".xlsx",index=None)

    data5_to_save=empty_df_to_fill_trial["name_offered"].value_counts(normalize=True).to_frame()
    data5_to_save.columns=["percent_share"]
    data5_to_save["strategy"]=data5_to_save.index.values

    data5_to_save.to_excel(path_to_save_output+"aggregate_data_consolidated_"+iteration_name+"_"+today+".xlsx",index=None)

    if len(fixed_agents) > 0:
        fixed_agents_data =empty_df_to_fill_trial.loc[empty_df_to_fill_trial["agent"].isin(fixed_agents)][["agent","name_offered","round","trial"]]
        fixed_agents_data=fixed_agents_data.sort_values(["agent","trial","round"])
        fixed_agents_data = fixed_agents_data.groupby("agent").first().reset_index()
        fixed_agents_data.to_excel(path_to_save_output+"fixedagents_data_detailed_"+iteration_name+"_"+today+".xlsx",index=None)

    parameters_pd = pd.DataFrame([{'iteration_name':iteration_name,'path_to_save_output':path_to_save_output,
                  'today':today,'num_neighbors':num_neighbors,'num_agents':num_agents,
                  'prob_edge_rewire':prob_edge_rewire,'grid_network_m':grid_network_m,
                  'grid_network_n':grid_network_n,'name_len':name_len,'num_of_rounds':num_of_rounds,
                  'num_of_trials':num_of_trials,'fixed_agents_ratio':fixed_agents_ratio,'perturb_ratio':perturb_ratio,
                  'cutoff_norms':cutoff_norms,'network_name':network_name,'random_seed':random_seed,
                  'function_to_use':function_to_use}]).T
    parameters_pd.columns=["parameter_values"]
    parameters_pd["parameter"]=parameters_pd.index
    parameters_pd[["parameter","parameter_values"]].to_excel(path_to_save_output+"parameters_"+iteration_name+"_"+today+".xlsx",index=None)
    
    return print("done")
