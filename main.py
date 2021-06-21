import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
from collections import Counter
import pickle

n_o_simluations = 100 # set simulation length,
# more is better but takes more time, ideal is 5.000 - 10.000 simulations
# which takes around 45 minutes on my laptop

opponent_matrix = {'ABCD':'D',
 'ABCE':'E',
'ABCF':'F',
'ABDE':'E',
'ABDF':'F',
'ABEF':'F',
'ACDE':'D',
'ACDF':'D',
'ACEF':'F',
'ADEF':'F',
'BCDE':'D',
'BCDF':'D',
'BCEF':'E',
'BDEF':'E',
'CDEF':'E'}

def calculate_prob_from_odds():
    odds["Prob Home"]=1/odds["Odds Home"]
    odds["Prob Draw"]=1/odds["Odds Draw"]
    odds["Prob Away"]=1/odds["Odds Away"]
    odds["Sum Odds"]=odds["Prob Away"]+odds["Prob Draw"]+odds["Prob Home"]
    odds["Prob Home"]/=odds["Sum Odds"]
    odds["Prob Draw"]/=odds["Sum Odds"]
    odds["Prob Away"]/=odds["Sum Odds"]
    odds["Sum Odds"]=odds["Prob Away"]+odds["Prob Draw"]+odds["Prob Home"]

def fill_h2h():
    for i in range(len(games_played)):
        game = games_played.loc[i]

        if game.Home_goals > game.Away_goals:
            standings.loc[standings.TEAMS==game.Home]["h2h"].apply(lambda x:x.append(game.Away))
        elif game.Home_goals < game.Away_goals:
            standings.loc[standings.TEAMS==game.Away]["h2h"].apply(lambda x:x.append(game.Home))

def play_game(game,standings_):
    """
    simulate the outcome off a game
    1. pick a (pseudo)random number between 0 and 1
    2. Based on this number and the probabilities of this game a result is determined
    3. Keep score of this result in the standings table
    """
    rand_nmr = random.random()

    standings_.loc[standings_.TEAMS==game['Home'],'MP'] += 1
    standings_.loc[standings_.TEAMS==game['Away'],'MP'] += 1

    if rand_nmr < game['Prob Home']:
        n_goals = goals() # a random number of goals is added to the goal tally, all games and in 1-0,2-0,3-0 or 4-0. This can be improved
        standings_.loc[standings_.TEAMS==game['Home'],'W'] += 1
        standings_.loc[standings_.TEAMS==game['Home'],'F'] += n_goals
        standings_.loc[standings_.TEAMS==game['Away'],'L'] += 1
        standings_.loc[standings_.TEAMS==game['Away'],'A'] += n_goals
        standings_.loc[standings_.TEAMS==game['Home']]["h2h"].apply(lambda x:x.append(game['Away']))

        return 0

    elif rand_nmr < game['Prob Home'] + game['Prob Draw']:
        # all draws end in 0-0 this can be improved
        standings_.loc[standings_.TEAMS==game['Home'],'D'] += 1
        standings_.loc[standings_.TEAMS==game['Away'],'D'] += 1

        return 1

    else:
        n_goals = goals() # a random number of goals is added to the goal tally, all games and in 1-0,2-0,3-0 or 4-0. This can be improved
        standings_.loc[standings_.TEAMS==game['Away'],'W'] += 1
        standings_.loc[standings_.TEAMS==game['Away'],'F'] += n_goals
        standings_.loc[standings_.TEAMS==game['Home'],'A'] += 1
        standings_.loc[standings_.TEAMS==game['Home'],'L'] += n_goals
        standings_.loc[standings_.TEAMS==game['Away']]["h2h"].apply(lambda x:x.append(game['Home']))

        return 2

def goals():
    """
    randomly picks a number of goals for the winning side.
    Should follow a poisson distribution without the zero.
    I guessed this; maybe a bit on the high side
    """
    rand_nmr = random.random()
    if rand_nmr < 0.5:
        return 1
    elif rand_nmr < 0.8:
        return 2
    elif rand_nmr < 0.97:
        return 3
    else:
        return 4

def find_opponent(standings,odds):
    """
    simulates the rest of the group stage
    sorts the standing following the tie breaker:
    1. Points
    2. Head to head
    3. Goal difference
    4. Goals scored
    5. number of wins
    returns the opponent of the dutch team following the opponent_matrix
    """

    # simulate all games
    for i in range(len(odds)):
        play_game(odds.loc[i],standings)

    # update the points and GD tally
    standings['P']=standings['W']*3 + standings['D']
    standings['GD']=standings['F']-standings['A']

    # see if teams have equal amount of points, and award h2h_points for
    # h2h results against those teams.
    for group in "ABCDEF":
        gelijk = standings.loc[standings['Group']==group][standings.loc[standings['Group']==group].duplicated(subset='P',keep=False)]
        gelijk["h2h_points"]=np.zeros(len(gelijk))

        for i in gelijk.index:
            for team1 in gelijk.loc[i]["h2h"]:
                for team2 in gelijk["TEAMS"]:
                    if team1==team2:
                        standings.loc[i,"h2h_points"]+=1

    # sort the final standings
    standings = standings.sort_values(by=['Group','P',"h2h_points",'GD','F','W'],ascending=[True,False,False,False,False,False])

    # determine third placed teams
    standings = standings.reset_index()
    third = standings.loc[[2,6,10,14,18,22]]

    # determine best number threes
    third = third.sort_values(by=['P','GD','F','W'],ascending=False)

    groups_of_best_no_3 = ""
    for i in third.head(4).Group:
        groups_of_best_no_3+=i
    groups_of_best_no_3 = ''.join(sorted(groups_of_best_no_3))

    # look up the opponent of the dutch team
    a = third.loc[third.Group == opponent_matrix[groups_of_best_no_3]]['TEAMS']

    return a.reset_index().TEAMS[0]

#read input data
standings = pd.read_csv("Standings.csv")
odds  = pd.read_csv("Odds.csv")
calculate_prob_from_odds()

# add columns to keep score on head to head results
h2h_ = []
for i in range(24): h2h_.append([])
standings["h2h"] = h2h_
standings["h2h_points"] = np.zeros(24) #points column, used later to sort for h2h results

games_played = pd.read_csv('game_results.csv')

opponents = []
# opponents = pickle.load( open( "opponents.p", "rb" ) ) # This can be used to include previous results to improve statistics

# do the simulations multiple times and remember the results
for i in range(n_o_simluations):
    fill_h2h()
    opponents.append(find_opponent(standings.copy(),odds))

    # ugly fix for emptying the h2h column after each round
    h2h_ = []
    for i in range(24): h2h_.append([])
    standings["h2h"]= h2h_

# save opponents in case you want to increase your statistics later
pickle.dump(opponents, open( "opponents.p", "wb" ) )

# count the occurences of each opponent and caculate the percentages
results = Counter(opponents)
for i in results.keys():
    results[i] = results[i]/float(len(opponents))*100

# sort results on size (seems to only work in python 3)
results=dict(sorted(results.items(), key=lambda x:x[1]))

#plot the results
plt.figure(facecolor='#FFFFFF') # set background to white otherise darkmode users will complain
plt.bar(range(len(results)), list(results.values()), align='center',color='orange')
plt.xticks(range(len(results)), list(results.keys()),rotation=90)
plt.title('Possible opponents Nederlands Elftal (%d simulations)'%(len(opponents)))
plt.ylabel('%')
plt.tight_layout()
plt.savefig("Opponents_NLD_EURO2020.jpg")
