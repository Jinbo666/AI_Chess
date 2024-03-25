from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.env_util import make_vec_env
# from sb3_contrib import MaskablePPO
# from sb3_contrib.common.maskable.callbacks import MaskableEvalCallback
from envs.chess_env import ChineseChessEnv  # 确保正确导入你的环境
from game.board import Board
import threading
import numpy as np
# from sb3_contrib.common.wrappers import ActionMasker
import torch
import matplotlib.pyplot as plt


print("PyTorch Version:", torch.__version__)
print(torch.cuda.is_available())
print(torch.cuda.device_count())
print(torch.cuda.get_device_name(0))
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print('device:', device)


import pygame
# 初始化pygame
print('pygame.init()...')
pygame.init()


board = Board(pygame)

# 设置共享状态用于控制渲染
render_requested = threading.Event()

RENDER_DELAY = 0
# 渲染间隔（你可能不再需要这个，因为渲染由主循环控制）
RENDER_EVERY = 1.0 / 60.0  # 假设我们目标是每秒渲染60帧
TOTAL_TIMESTEPS = 10000000


# def action_mask_fn(env):
#     # 根据环境状态返回动作掩码
#     # 这里是一个示例，具体实现应该基于你的环境
#     # 假设有90个可能的动作，随机选择一些动作为无效动作
#     action_mask = np.ones(90*90, dtype=np.bool)
#     action_mask[np.random.choice(90*90, size=20, replace=False)] = False
#     return action_mask


# 创建环境
# num_envs = 16  # 并行环境的数量
# env = ChineseChessEnv(board, render_delay=RENDER_DELAY)

# 假设你需要传递额外的参数给你的环境，你可以通过`env_kwargs`参数来提供
env_kwargs = {"board": board, "render_delay": RENDER_DELAY}  # 这里的None是一个占位符，你需要根据实际情况调整
# 创建并行环境，这里的`env_id`参数是你的环境类
env = make_vec_env(env_id=ChineseChessEnv, n_envs=16, env_kwargs=env_kwargs)

# # 使用ActionMasker包装器来添加动作掩码支持
# env = ActionMasker(env, action_mask_fn)

class TrainingCallback(BaseCallback):
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.episode_rewards = []
        self.episode_lengths = []
        self.last_episode = 0

    def _on_step(self) -> bool:
        # print('TrainingCallback _on_step')
        # 每一步都会调用这个方法
        # 检查是否有情节结束的信息

        if 'episode' in self.locals and self.locals['episode'] > self.last_episode:
            print('================episode:', self.locals.get('episode', 0))
            self.episode_rewards.append(self.locals['episode']['r'])
            # self.episode_lengths.append(self.locals['episode']['l'])
            # 每当累积足够多的情节后，计算平均累计奖励并更新图表
            self._update_plot()

            self.last_episode = self.locals['episode']
        return True

    def _update_plot(self):
        plt.figure(1)
        plt.clf()
        plt.title('Training Progress')
        plt.xlabel('Episode')
        plt.ylabel('Reward')
        plt.plot(self.episode_rewards)
        plt.pause(1)  # pause a bit so that plots are updated

def train_model(env):
    policy_kwargs = dict(
        net_arch=[dict(pi=[256, 256, 256, 256], vf=[256, 256, 256, 256])]
    )
    model = PPO("MlpPolicy", env, verbose=1,
                n_steps=4096,  # 每次更新模型前收集的时间步数
                batch_size=8192,  # 每个小批量的大小（对于PPO，这通常是通过n_steps和n_minibatch间接控制）
                policy_kwargs=policy_kwargs
                )
    # model.to(device)

    # # 创建MaskableEvalCallback实例
    # eval_callback = MaskableEvalCallback(env, best_model_save_path='./model/',
    #                                      log_path='./logs/', eval_freq=500,
    #                                      deterministic=True, render=False)

    # 计算总参数数量
    total_params = sum(p.numel() for p in model.policy.parameters() if p.requires_grad)
    print(f"Total trainable parameters: {total_params}")

    # 开始训练
    print("Starting model.learn")
    model.learn(total_timesteps=TOTAL_TIMESTEPS, callback=TrainingCallback())

    print("Model training completed.")
    model.save("ppo_chinese_chess")
    print("Model saved.")

# 直接在主循环中启动训练，并处理渲染和事件
def main_loop():
    last_render_time = 0
    RENDER_EVERY = 1.0 / 60.0  # 假设我们目标是每秒渲染60帧

    # 启动模型训练
    train_model(env)

    # 训练完成后，继续运行Pygame事件循环和渲染，或者直接退出
    try:
        while True:
            # env.render() # 如果你的环境支持渲染
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
    except KeyboardInterrupt:
        print("Exiting...")
        pygame.quit()

main_loop()





#===========================================================================================
'''
class TrainingCallback(BaseCallback):
    def __init__(self, render_every=RENDER_EVERY, verbose=0):
        super().__init__(verbose)
        self.render_every = render_every

    def _on_step(self) -> bool:
        print('TrainingCallback _on_step')
        return True
    
should_stop = threading.Event()  # 控制训练停止的事件

def train_model(env, callback):
    model = PPO("MlpPolicy", env, verbose=1)

    # 创建一个回调，用于检查是否应该停止训练
    class StopTrainingCallback(BaseCallback):
        def __init__(self):
            super(StopTrainingCallback, self).__init__()

        def _on_step(self) -> bool:
            return not should_stop.is_set()  # 如果should_stop被设置，则停止训练

    # 将StopTrainingCallback和其他回调结合起来
    combined_callbacks = CallbackList([callback, StopTrainingCallback()])
    try:
        # 开始训练，训练过程会自动检查是否需要停止
        # 训练模型前的日志
        print("Starting model.learn")
        model.learn(total_timesteps=10000, callback=combined_callbacks)
        # 训练模型后的日志
        print("Model training completed.")
    except Exception as e:
        print(f"Training interrupted: {e}")
    finally:
        model.save("ppo_chinese_chess")
        print("Model saved.")


# 主线程运行的主循环
def main_loop():
    last_render_time = 0
    try:
        while True:
            current_time = pygame.time.get_ticks()
            if current_time - last_render_time > RENDER_EVERY * 1000:
                env.render()
                last_render_time = current_time
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
    except KeyboardInterrupt:
        print("Stopping training and exiting...")
        # 这里可以添加任何清理代码，比如停止后台线程
        should_stop.set()  # 通知训练线程停止
        training_thread.join()  # 现在应该能够更快地结束了
        pygame.quit()
        # 如果有其他需要清理的资源，也可以在这里处理
# 在独立线程中启动训练
training_thread = threading.Thread(target=train_model, args=(env, TrainingCallback()))
training_thread.daemon = True  # 将线程设置为守护线程
training_thread.start()

# 在主线程中运行Pygame事件循环和渲染
main_loop()

# 等待训练线程结束
training_thread.join()
'''