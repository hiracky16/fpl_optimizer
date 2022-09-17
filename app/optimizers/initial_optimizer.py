import pandas as pd, pulp, logging, json
from .const import (
    POSITIONS,
    PLAYER_LIMIT_BY_POSITIONS,
    TOTAL_PLAYERS,
    SAME_TEAM_LIMIT,
    COST_LIMIT
)
FAVORIT_TEAMS = ['Man Utd']
# EXCLUSIVE TEAMS
EXCLUSIVE_TEAMS = ['West Ham']
# output columns
OUTPUT_COLUMNS = ['id', 'name', 'element_type_name', 'team_name', 'total_points', 'now_cost']

def read_elements():
    return pd.read_csv('data/elements.csv')

def set_variables(data):
    fun = lambda x: pulp.LpVariable(f'{x.id}_{x.element_type_name}_{x.team_name}', cat='Binary')
    data['variables'] = list(data.apply(fun, axis=1))
    return data

def solve(data):
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
    return data

def selected_elements(data):
    result = data[data.flag == 1].sort_values('element_type_name')
    objects = { 'elements': result[OUTPUT_COLUMNS].to_dict(orient='records') }
    return json.dumps(objects)

def main():
    data = read_elements()
    data = set_variables(data)
    result = solve(data)
    return selected_elements(data)

if __name__ == "__main__":
    res = main()
    print(res)