

# from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from envs.chess_env import ChineseChessEnv  # 确保正确导入你的环境
from game.board import Board

import pygame
# 初始化pygame
print('pygame.init()...')
pygame.init()


board = Board(pygame)
# 创建环境实例
# env = make_vec_env(lambda: ChineseChessEnv(board), n_envs=1)

# 创建环境
env = ChineseChessEnv(board)

class RenderCallback(BaseCallback):
    """
    自定义回调来在训练过程中渲染环境
    """
    def __init__(self, render_every: int = 100, verbose: int = 0):
        super(RenderCallback, self).__init__(verbose)
        self.render_every = render_every  # 每多少步渲染一次

    def _on_step(self) -> bool:
        if self.n_calls % self.render_every == 0:
            env.render()  # 调用环境的渲染方法
            # import time
            # time.sleep(1)
        return True  # 返回True确保训练继续
    
def train_model():


    # 创建模型实例
    model = PPO("MlpPolicy", env, verbose=1)

    
    # 创建渲染回调实例
    render_callback = RenderCallback(render_every=1000)  # 每100个训练步骤渲染一次

    
    # 训练模型
    model.learn(total_timesteps=1000000, callback=render_callback)

    # 可以保存模型进行以后使用
    model.save("ppo_chinese_chess")
    

if __name__ == "__main__":
    train_model()
