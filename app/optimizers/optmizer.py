import pandas as pd
import requests
import pulp, logging, json
from .const import (
    PLAYER_LIMIT_BY_POSITIONS,
    SAME_TEAM_LIMIT,
    TOTAL_PLAYERS,
    COST_LIMIT
)
from .repository import Repository

# 交代選手数
REPLACEMENT = 3

FAVORIT_TEAMS = []
# EXCLUSIVE TEAMS
EXCLUSIVE_TEAMS = []

OUTPUT_COLUMNS = ['id', 'element_type_name', 'name', 'expected_points', 'now_cost']

def get_current_team(id: int, event: int):
    """現在のチーム選手を取得する
    Args:
        id (int): チームID
    Returns:
        DataFrame: 現状の選手一覧
    """
    res = requests.get(f'https://fantasy.premierleague.com/api/entry/{id}/event/{event}/picks/')
    obj = json.loads(res.text)
    elements = obj['picks']
    return pd.json_normalize(elements)

def get_least_elements_stas():
    repository = Repository()
    return repository.read_expected_elements()

def current_team(team_id, event):
    master = get_least_elements_stas()
    current = get_current_team(team_id, event)
    current = master.merge(current, left_on='id', right_on='element')
    return {'current': current[OUTPUT_COLUMNS].to_dict(orient='records')}

def optimize(current: pd.DataFrame, master: pd.DataFrame, replacement: int=1):
    print(replacement)
    fun = lambda x: pulp.LpVariable(f'{x.id}_{x.element_type_name}_{x.team_name}', cat='Binary')
    master['variables'] = list(master.apply(fun, axis=1))
    prob = pulp.LpProblem('fpl_planner', sense = pulp.LpMaximize)
    # ポジションごとの人数の制約
    for p in master.element_type_name.unique():
        dt = master[master.element_type_name == p]
        prob += pulp.lpSum(dt.variables) == PLAYER_LIMIT_BY_POSITIONS[p]

    # 同じチーム 3 人の制約
    for t in master.team_name.unique():
        dt = master[master.team_name == t]
        prob += pulp.lpSum(dt.variables) <= SAME_TEAM_LIMIT

    # お気に入りチーム選手を絶対一人入れる
    for t in FAVORIT_TEAMS:
        dt = master[master.team_name == t]
        prob += pulp.lpSum(dt.variables) >= 1

    # 交代選手数
    dt = master[master.id.isin(current.element.values)]
    prob += pulp.lpSum(dt.variables) == TOTAL_PLAYERS - replacement

    # 目的関数
    prob += pulp.lpDot(master.expected_points, master.variables)
    # コストの制限
    prob += pulp.lpDot(master.now_cost, master.variables) <= COST_LIMIT
    # 全体の選手数の制限
    prob += pulp.lpSum(master.variables) == TOTAL_PLAYERS

    status = prob.solve()
    print("Status", pulp.LpStatus[status])
    print(prob.objective.value())
    expected_points = prob.objective.value() - (4 * (replacement - 1))
    master['flag'] = master.apply(lambda x: x.variables.value(), axis=1)
    expected = master[master.flag == 1].sort_values('element_type_name')
    current = master.merge(current, left_on='id', right_on='element')
    in_elements = expected[~expected['id'].isin(current.element.values)]
    out_elements = current[~current['element'].isin(expected.id.values)]
    return {
        'expected_points': expected_points,
        'out_elements': out_elements[OUTPUT_COLUMNS].to_dict(orient='records'),
        'in_elements': in_elements[OUTPUT_COLUMNS].to_dict(orient='records'),
        'current': current[OUTPUT_COLUMNS].to_dict(orient='records')
    }

def main(team_id, event, replacement=1):
    current = get_current_team(team_id, event)
    master = get_least_elements_stas()
    return optimize(current, master, replacement)

if __name__ == "__main__":
    res = main(team_id=2555500, event=5, replacement=3)
    # res = current_team(team_id=2555500, event=5)
    print(res)