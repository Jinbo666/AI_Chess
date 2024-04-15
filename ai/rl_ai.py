from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.env_util import make_vec_env
from envs.chess_env import ChineseChessEnv  # 确保正确导入你的环境
from game.board import Board
from ai.mcts import do_mcts
import threading
import torch
import pygame


print("PyTorch Version:", torch.__version__)
print(torch.cuda.is_available())
print(torch.cuda.device_count())
print(torch.cuda.get_device_name(0))
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print('device:', device)


# 初始化pygame
print('pygame.init()...')
pygame.init()
board = Board(pygame)
TOTAL_TIMESTEPS = 10000000


RENDER_DELAY = 1
# 渲染间隔（你可能不再需要这个，因为渲染由主循环控制）
RENDER_EVERY = 1.0 / 60.0  # 假设我们目标是每秒渲染60帧
env_kwargs = {"board": board, "render_delay": RENDER_DELAY}  # 这里的None是一个占位符，你需要根据实际情况调整
env = make_vec_env(env_id=ChineseChessEnv, n_envs=1, env_kwargs=env_kwargs)



class TrainingCallback(BaseCallback):
    def __init__(self,  render, env, verbose=0):
        super().__init__(verbose)
        self.episode_rewards = []

    def _on_step(self) -> bool:
        return True

def encode_action(start_x, start_y, end_x, end_y):
    board_width = 9
    board_height = 10
    total_positions = board_width * board_height

    start_pos = start_y * board_width + start_x
    end_pos = end_y * board_width + end_x

    action_index = start_pos * total_positions + end_pos
    return action_index


def train_model_with_mcts(env, render=False):
    model = PPO("MlpPolicy", env, verbose=1, n_steps=2048, batch_size=64)
    obs = env.reset()[0]
    print('obs:', obs)
    print(obs.shape)
    if render:
        env.render()  # 初始渲染

    for step in range(TOTAL_TIMESTEPS):
        current_board = env.get_attr('board')[0]  # 获取 board 对象
        # print('current_board:', current_board)
        # 获取当前玩家颜色
        current_color = current_board.current_player
        # print('current_color:', current_color)

        best_action = do_mcts(obs, current_color, current_board, iterations=100)  # 使用MCTS
        print('best_action:', best_action)
        start_x, start_y, end_x, end_y = best_action
        best_action_index = encode_action(start_x, start_y, end_x, end_y)
        print('best_action_index:', best_action_index)
        obs, rewards, dones, info = env.step([best_action_index])

        if render:
            env.render()  # 每次动作后渲染新的状态

        if dones.any():  # 注意: 当使用 make_vec_env 时, dones 是一个数组
            obs = env.reset()

        # 检查是否完成足够的步骤后进行学习
        if (step + 1) % 2048 == 0 or step == TOTAL_TIMESTEPS - 1:
            model.learn(total_timesteps=2048)

    model.save("ppo_chinese_chess_mcts")
    print("Model training with MCTS completed and saved.")


def train_model(env, render=False):
    # policy_kwargs = dict(
    #     net_arch=[dict(pi=[256, 256, 256, 256], vf=[256, 256, 256, 256])]
    # )
    model = PPO("MlpPolicy", env, verbose=1,
                n_steps=2048,  # 4096 每次更新模型前收集的时间步数
                batch_size=64,  # 8192 每个小批量的大小（对于PPO，这通常是通过n_steps和n_minibatch间接控制）
                )
    # 计算总参数数量
    total_params = sum(p.numel() for p in model.policy.parameters() if p.requires_grad)
    print(f"Total trainable parameters: {total_params}")

    # 开始训练
    print("Starting model.learn")
    model.learn(total_timesteps=TOTAL_TIMESTEPS, callback=TrainingCallback(render=render, env=env))
    print("Model training completed.")
    model.save("ppo_chinese_chess")
    print("Model saved.")

def render_loop(env):
    try:
        while True:
            if hasattr(env, 'envs'):
                for single_env in env.envs:
                    # print('called on render_loop!')
                    single_env.render()  # 确保对每个环境实例调用render
            else:
                env.render()  # 如果env不是向量环境，则直接调用render
            pygame.display.flip()  # 确保屏幕更新
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            pygame.time.wait(10)  # 控制渲染频率，防止过快渲染
    except KeyboardInterrupt:
        pygame.quit()


# 直接在主循环中启动训练，并处理渲染和事件
def main_loop():
    # 创建一个线程用于模型训练
    training_thread = threading.Thread(target=train_model_with_mcts, args=(env, True))  # (target=train_model, args=(env,))
    training_thread.start()
    # 主线程用于渲染
    # render_loop(env)
    # training_thread.join()  # 等待训练线程结束
    pygame.quit()

main_loop()