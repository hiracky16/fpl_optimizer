import os

# const
# Position name
POSITIONS = ['GKP', 'DEF', 'MID', 'FWD']
# Limit on the number of players by position
PLAYER_LIMIT_BY_POSITIONS = {'GKP': 2, 'DEF': 5, 'MID': 5, 'FWD': 3}
# Limit on the number of players
TOTAL_PLAYERS = sum([p for p in PLAYER_LIMIT_BY_POSITIONS.values()])
STARTING_TOTAL_PLAYERS = 11
# Limit on the number of players on the same team
SAME_TEAM_LIMIT = 3
# Limit on cost
COST_LIMIT = 1000

# 環境変数
IS_GCS = os.environ.get('IS_GCS') == 'TRUE'
DATAMART_BUCKET = os.environ.get('DATAMART_BUCKET')