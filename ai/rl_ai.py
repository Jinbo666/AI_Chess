

# from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback, CallbackList
from envs.chess_env import ChineseChessEnv  # 确保正确导入你的环境
from game.board import Board
import threading
import time

import pygame
# 初始化pygame
print('pygame.init()...')
pygame.init()


board = Board(pygame)

# 设置共享状态用于控制渲染
render_requested = threading.Event()


# 创建环境
env = ChineseChessEnv(board, render_delay=0.5)

# 渲染间隔（你可能不再需要这个，因为渲染由主循环控制）
render_every = 1.0 / 60.0  # 假设我们目标是每秒渲染60帧

class TrainingCallback(BaseCallback):
    def __init__(self, render_every=100, verbose=0):
        super().__init__(verbose)
        self.render_every = render_every

    def _on_step(self) -> bool:
        # 这里我们不直接请求渲染，而是让主循环按自己的节奏渲染
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

    # 开始训练，训练过程会自动检查是否需要停止
    model.learn(total_timesteps=10000, callback=combined_callbacks)

    # 保存模型
    model.save("ppo_chinese_chess")


# 主线程运行的主循环
def main_loop():
    last_render_time = 0
    try:
        while True:
            current_time = pygame.time.get_ticks()
            if current_time - last_render_time > render_every * 1000:
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
# training_thread = threading.Thread(target=train_model, args=(env, TrainingCallback()))
# training_thread.start()
training_thread = threading.Thread(target=train_model, args=(env, TrainingCallback()))
training_thread.daemon = True  # 将线程设置为守护线程
training_thread.start()


# 在主线程中运行Pygame事件循环和渲染
main_loop()

# 等待训练线程结束
training_thread.join()

# class RenderCallback(BaseCallback):
#     """
#     自定义回调来在训练过程中渲染环境
#     """
#     def __init__(self, render_every: int = 100, verbose: int = 0):
#         super(RenderCallback, self).__init__(verbose)
#         self.render_every = render_every  # 每多少步渲染一次

#     def _on_step(self) -> bool:
#         if self.n_calls % self.render_every == 0:
#             # env.render()  # 调用环境的渲染方法
#             pass
#         return True  # 返回True确保训练继续
    
# def train_model():


#     # 创建模型实例
#     model = PPO("MlpPolicy", env, verbose=1)

    
#     # 创建渲染回调实例
#     render_callback = RenderCallback(render_every=100)  # 每100个训练步骤渲染一次

    
#     # 训练模型
#     try:
#         model.learn(total_timesteps=10000, callback=render_callback)
#     finally:

    
#         # 停止渲染线程
#         render_thread.stop()
#         render_thread.join()  # 等待渲染线程结束

#         # 可以保存模型进行以后使用
#         model.save("ppo_chinese_chess")
    

# if __name__ == "__main__":
#     train_model()
