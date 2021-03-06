import torch
import torch.nn as nn
import configparser
print("DEVICES", torch.cuda.device_count())
print("__________________________")
config = configparser.RawConfigParser()
config.read("/home/startupshell/Desktop/Sander/GLADIATOR-Project/ray_config.cfg")
print(config)
import os
paths = dict(config.items('PATHS'))
print(paths)
import sys
sys.path.append(os.getcwd()) 
sys.path.append("/home/startupshell/Desktop/Sander/GLADIATOR-Project/environment")
import ray
ray.init(runtime_env={"working_dir": "/home/startupshell/Desktop/Sander/GLADIATOR-Project"})

sys.path.append("..")
sys.path.append(paths["glob"])
sys.path.append(paths["work"])
import ray
ray.init(runtime_env={"working_dir": paths["work"]})
from ray.rllib.agents.ppo import PPOTrainer
from ray.rllib.agents import ppo
from ray.rllib.models import ModelCatalog
from ray.tune.registry import register_env
from ray.rllib.agents.ppo import PPOTrainer


from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
from ray.rllib.models.torch.misc import normc_initializer, same_padding, \
    SlimConv2d, SlimFC
from ray.rllib.models.utils import get_activation_fn, get_filter_config
from ray.rllib.utils.annotations import override
from ray.rllib.utils.framework import try_import_torch
from ray.rllib.utils.typing import ModelConfigDict, TensorType
from environment.dummy_spec import DummyGym
from environment.dummy_spec import DummyMAGym
from environment.pvpbox_specs import PvpBox
from environment.wrappers import *

from ray import tune
#import pyspiel
#from open_spiel.python.rl_environment import Environment
#from ray.rllib.env.wrappers.open_spiel import OpenSpielEnv


agent_actions = [("attack", 1), ("left", 1), ("back", 1), ("right", 1), ("forward", 1), ("camera", [0,15]), ("camera", [0,-15])]
num_actions = len(agent_actions)
def env_creator(env_config):
    # return DummyGym()
    return OneVersusOneWrapper(SuperviserWrapper(PvpBox(agent_count=2).make(instances=[])), agent_actions)
            
    # return CartPoleEnv()
    # env = OneVersusOneWrapper(PvpBox(agent_count=2).make(instances=[]))
    # opponent = Agent(Discrete_PPO_net(num_actions), False)
    # env = OpponentStepWrapper(env, opponent, agent_actions)

register_env("1v1env", env_creator)

from model import Discrete_PPO_net
# ModelCatalog.register_custom_model("cnet", Net)
ModelCatalog.register_custom_model("cnet", Discrete_PPO_net)

# Configure the algorithm.
config = {
    # Environment (RLlib understands openAI gym registered strings).
    "env": "1v1env",
    # Use 2 environment workers (aka "rollout workers") that parallelly
    # collect samples from their own environment clone(s).
    # "num_workers": 2,
    # Change this to "framework: torch", if you are using PyTorch.
    # Also, use "framework: tf2" for tf2.x eager execution.
    "framework": "torch",
    # Tweak the default model provided automatically by RLlib,
    # given the environment's observation- and action spaces.
    "model": {
        "custom_model": "cnet",
        # Extra kwargs to be passed to your model's c'tor.
        "custom_model_config": {},
    },
    "multiagent": {
        "policies": {
            "policy_01": (None, DummyMAGym(len(agent_actions)).observation_space, DummyMAGym(len(agent_actions)).action_space, {}),
            "policy_02": (None, DummyMAGym(len(agent_actions)).observation_space, DummyMAGym(len(agent_actions)).action_space, {}),
        },
        "policy_mapping_fn": lambda agent_id:
            "policy_01" if agent_id == "agent_0" else "policy_02",

       "policies_to_train": ["policy_01"]
    },
    "rollout_fragment_length": 80,
    "train_batch_size": 240,
    "sgd_minibatch_size": 80,
    "num_gpus": 1,
    "ignore_worker_failures": True,
    # Set up a separate evaluation worker set for the
    # `trainer.evaluate()` call after training (see below).
    # "evaluation_num_workers": 1,
    # # Only for evaluation runs, render the env.
    # "evaluation_config": {
    #     "render_env": True,
    # }
}
analysis = tune.run(
    "PPO",
    name="MINE_PPO",
    config=config,
    #checkpoint_freq=100,
    local_dir="ray_out",
    #stop={"episode_reward_mean": 50},
)
# trainer = PPOTrainer(config=config)
# trainer.restore("ray_out/checkpoint_003001/checkpoint-3001")
# # Create our RLlib Trainer.
# for i in range(200000):
#     trainer.train()
#     print("TRAINER TRAINED", i)
#     # if i % 1 == 0:
#     #     trainer.set_weights({
#     #         "policy_02": trainer.get_weights(["policy_01"])["policy_01"], 
#     #     })
#     if i % 100 == 0:
#         checkpoint = trainer.save("ray_out")
# checkpoint = trainer.save("ray_out")   
   #print("checkpoint saved at", checkpoint)
# print(trainer.get_weights(["policy_01"]))

# Evaluate the trained Trainer (and render each timestep to the shell's
# output).
# trainer.evaluate()
print("DONE")
