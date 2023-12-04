import numpy as np
import random
import gym
import warnings
import pickle
import register_env
from rl_car_env import RlCarEnv

def initialize_q_table(state_space, action_space):
    Qtable = np.zeros((state_space + [action_space])) 
    return Qtable

def epsilon_greedy_policy(Qtable, state, epsilon):
    random_int = random.uniform(0, 1)
    if random_int > epsilon:
        action = np.argmax(Qtable[tuple(state)]) # exploit
    else:
        action = env.action_space.sample() # explore
    return action

def greedy_policy(Qtable, state):
    action = np.argmax(Qtable[state])
    return action

def train(n_training_episodes, min_epsilon, max_epsilon, decay_rate, env, max_steps, Qtable):
    for episode in range(n_training_episodes):
        epsilon = min_epsilon + (max_epsilon - min_epsilon)*np.exp(-decay_rate*episode)
        #Reset the environment
        state = env.reset()
        # repeat
        for step in range(max_steps):
            print(f"Episode {episode}/{n_training_episodes} step {step}")
            action = epsilon_greedy_policy(Qtable, state, epsilon)
            new_state, reward, _, _, _ = env.step(action) # Terminated, Truncated, Info are not needed
            env.render()

            # custom indexing for state and action 
            state_action = tuple(np.append(state, action))
            new_state_action = tuple(np.append(new_state, action))

            Qtable[state_action] = Qtable[state_action] + learning_rate * (reward + gamma * np.max(Qtable[new_state_action]) - Qtable[state_action])
            
            state = new_state
            
    env.close()
    return Qtable

def evaluate_agent(env, max_steps, n_eval_episodes, Q, seed):
    episode_rewards = []
    for episode in range(n_eval_episodes):
        if seed:
            state = env.reset(seed=seed[episode])
        else:
            state = env.reset()
            total_rewards_ep = 0
    
        for step in range(max_steps):
            # Take the action (index) that have the maximum reward
            action = np.argmax(Q[state][:])
            new_state, reward, _, _, _= env.step(action)
            total_rewards_ep += reward
            
            state = new_state
        episode_rewards.append(total_rewards_ep)
    mean_reward = np.mean(episode_rewards)
    std_reward = np.std(episode_rewards)

    return mean_reward, std_reward

warnings.filterwarnings("ignore", category=UserWarning, module="gym")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="gym")

env = gym.make("RlCar-v0")

print("Observation Space", env.observation_space)
print("Sample observation", env.observation_space.sample())

print("Action Space Shape", env.action_space.n)
print("Action Space Sample", env.action_space.sample())

discrete_os_size = [21, 21, 21, 21, 21, 11]
action_space = env.action_space.n

# Training parameters
n_training_episodes = 1000
learning_rate = 0.7        

# Evaluation parameters
n_eval_episodes = 100      

# Environment parameters
env_id = "RlCar-v0"   
max_steps = 2000
gamma = 0.95               
eval_seed = []             

# Exploration parameters
max_epsilon = 1.0           
min_epsilon = 0.05           
decay_rate = 0.0005

# Qtable_rlcar = initialize_q_table(discrete_os_size, action_space)

# # Start training
# Qtable_rlcar = train(n_training_episodes, min_epsilon, max_epsilon, decay_rate, env, max_steps, Qtable_rlcar)


# print(Qtable_rlcar)

# with open('q_table.pkl', 'wb') as f:
#     pickle.dump(Qtable_rlcar, f)

with open('q_table.pkl', 'rb') as f:
    Qtable_rlcar = pickle.load(f)

# Evaluate our Agent
mean_reward, std_reward = evaluate_agent(env, max_steps, n_eval_episodes, Qtable_rlcar, eval_seed)
print(f"Mean_reward={mean_reward:.2f} +/- {std_reward:.2f}")