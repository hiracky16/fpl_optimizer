import pandas as pd
import pulp, logging

data = pd.read_csv('data.csv')

# const
# Position name
POSITIONS = ['GKP', 'DEF', 'MID', 'FWD']
# Limit on the number of players by position
PLAYER_LIMIT_BY_POSITIONS = {'GKP': 2, 'DEF': 5, 'MID': 5, 'FWD': 3}
# Limit on the number of players
TOTAL_PLAYERS = sum([p for p in PLAYER_LIMIT_BY_POSITIONS.values()])
# Limit on the number of players on the same team
SAME_TEAM_LIMIT = 3
# Limit on cost
COST_LIMIT = 970
# favorit team （default: none）
# FAVORIT_TEAM = 'Man Utd'
FAVORIT_TEAMS = ['Man Utd']
# EXCLUSIVE TEAMS
EXCLUSIVE_TEAMS = ['West Ham']


fun = lambda x: pulp.LpVariable(f'{x.id}_{x.element_type_name}_{x.team_name}', cat='Binary')
data['variables'] = list(data.apply(fun, axis=1))

# 制約
prob = pulp.LpProblem('fpl_planner', sense = pulp.LpMaximize)
# ポジションごとの人数の制約
for p in data.element_type_name.unique():
    dt = data[data.element_type_name == p]
    prob += pulp.lpSum(dt.variables) == PLAYER_LIMIT_BY_POSITIONS[p]

# 同じチーム 3 人の制約
for t in data.team_name.unique():
    dt = data[data.team_name == t]
    prob += pulp.lpSum(dt.variables) <= SAME_TEAM_LIMIT

# お気に入りチーム選手を絶対一人入れる
for t in FAVORIT_TEAMS:
    dt = data[data.team_name == t]
    prob += pulp.lpSum(dt.variables) >= 1

# 除外するチーム
for t in EXCLUSIVE_TEAMS:
    dt = data[data.team_name == t]
    prob += pulp.lpSum(dt.variables) == 0

# 目的関数
prob += pulp.lpDot(data.total_points, data.variables)
# コストの制限
prob += pulp.lpDot(data.now_cost, data.variables) <= COST_LIMIT
# 全体の選手数の制限
prob += pulp.lpSum(data.variables) == TOTAL_PLAYERS

status = prob.solve()
logging.info("Status", pulp.LpStatus[status])
logging.info(prob.objective.value())

data['flag'] = data.apply(lambda x: x.variables.value(), axis=1)
result = data[data.flag == 1].sort_values('element_type_name')
result.to_json(orient='records')