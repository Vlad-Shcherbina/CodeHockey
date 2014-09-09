import sys
sys.path.append('../strategy')
sys.path.append('../python3-cgdk')

# for recorder.py
sys.path.append('../replay_utils')

# here we import strategy/MyStrategy.py,
# even though there is also in python3-cgdk/MyStrategy
import MyStrategy

# actually runs stuff
import Runner
