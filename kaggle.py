from kaggle_environments import make
from agent import agent
from pathlib import Path

Path(__file__).with_name("agent_debug.log").write_text("", encoding="utf-8")
env = make('kaggriculture', debug=True)

env.run([agent, 'random'])

import json
with open("replay.json", "w") as f:
    json.dump(env.toJSON(), f)
