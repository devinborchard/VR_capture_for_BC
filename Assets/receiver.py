#add to robosuite in robosuite/demos folder
#may need to allow port through firwall

import socket
import numpy as np
import robosuite as suite
from robosuite.wrappers import GymWrapper
import time
from scipy.spatial.transform import Rotation as R
from robosuite.controllers import controller_factory




# === UDP Receiver Setup ===
UDP_IP = "0.0.0.0"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)


def setup_env():




   env = suite.make(
       env_name="Lift",
       robots="Panda",
       has_renderer=True,
       has_offscreen_renderer=False,
       use_camera_obs=False,
       control_freq=20,
   )
   return env


# def unity_to_mujoco_quat(unity_quat):
#     # Unity quaternion is [x, y, z, w], and Unity uses a left-handed coordinate system
#     # Convert Unity -> MuJoCo (right-handed): Apply coordinate transform
#     r = R.from_quat(unity_quat)
#     transform = R.from_euler('xyz', [-90, 0, -90], degrees=True)
#     mujoco_rot = transform * r
#     return mujoco_rot


def step(env, obs, pos_action, rot_action, grip_action):
   pos_action = pos_action * 90
   # pos_action = np.zeros(3)
   rot_action = np.zeros(3)
   # axis_angle = axis_angle * 10
   # axis_angle = np.zeros(3)
   # print("rot_action: ", rot_action)
   action = np.concatenate([pos_action, rot_action, [grip_action]])
   obs, reward, done, _ = env.step(action)
   env.render()
   time.sleep(1 / 20.0)
   return obs


def read_latest_udp(sock):
   latest_data = None
   while True:
       try:
           data, _ = sock.recvfrom(1024)
           latest_data = data
       except BlockingIOError:
           break
   return latest_data


def main():
   env = setup_env()
   obs = env.reset()
   print("Robosuite environment started.")


   last_pos = None
   last_rot = None
   last_quat = None


   while True:
       pos_action = np.zeros(3)
       rot_action = np.zeros(3)
       axis_angle = np.zeros(3)
       trigger = 0
       enable = 0


       data = read_latest_udp(sock)
       if data:
           msg = data.decode("utf-8")
           values = list(map(float, msg.strip().split(",")))
           if len(values) == 12:
               # Unity sends position as (z, x, y)
               target_pos = np.array([values[0], values[1], values[2]])
               unity_quat = np.array(values[3:7])  # Unity [x, y, z, w]
               target_rot = np.array(values[7:10])
               enable = values[10]
               trigger = values[11]


               # print('-------------')
               # print("enable ", enable)
               if enable:
                   if last_pos is not None:
                       pos_action = target_pos - last_pos


                   if last_rot is not None:
                       rot_action = target_rot - last_rot
                   # Convert Unity quaternion to MuJoCo format and compute delta
                   # mujoco_quat = unity_to_mujoco_quat(unity_quat).as_quat()


                   # if last_quat is not None:
                   #     r_prev = R.from_quat(last_quat)
                   #     r_curr = R.from_quat(mujoco_quat)
                   #     r_delta = r_curr * r_prev.inv()
                   #     axis_angle = r_delta.as_rotvec()
                   # else:
                   #     axis_angle = np.zeros(3)


                   last_pos = target_pos
                   last_rot = target_rot
                   # last_quat = mujoco_quat


       obs = step(env, obs, pos_action, rot_action, trigger)


main()







