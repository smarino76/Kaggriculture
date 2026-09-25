from kaggle_environments import make
from agent import agent

env = make('kaggriculture', debug=True)

env.run([agent, 'random'])

import json
with open("replay.json", "w") as f:
    json.dump(env.toJSON(), f)
