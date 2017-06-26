import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)

register(
    id='gym-airsim-v0',
    entry_point='gym_airsim.envs:AirsimEnv',
    nondeterministic = True
)
