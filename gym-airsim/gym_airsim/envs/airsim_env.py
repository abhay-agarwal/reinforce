import os, subprocess, time, signal, sys
import numpy as np
import cv2
import gym
from gym import error, spaces
from gym import utils
from gym.utils import seeding

import docker
from .PythonClient import *

from vncdotool import api as vncapi

import logging
logger = logging.getLogger(__name__)

pi = 3.14159265483

Directions = {
    0: pi*(-5/10),
    1: pi*(-4/10),
    2: pi*(-3/10),
    3: pi*(-2/10),
    4: pi*(-1/10),
    5: 0,
    6: pi*(1/10),
    7: pi*(2/10),
    8: pi*(3/10),
    9: pi*(4/10),
    10:pi*(5/10),
}

default_reward = -1 # reward for matching A*

class AirsimEnv(gym.Env):

    metadata = {"render.modes": ["human","rgb_array"]}
    
    def __init__(self):

        self.steps = 0
        self.max_timesteps = 99
        self.total_episodes = 0

        # TODO continuous action space
        self.action_space = spaces.Discrete(11)
        self.observation_space = spaces.Box(low=0, high=255, shape=(42,42,1))

    def _assign(self, container_id):
        self.container_id = container_id
        self.name = "airsim-0%d" % container_id
        self.rpcport = 41450 + container_id
        try:
            self.container = docker.from_env().containers.get(self.name)
        except docker.errors.NotFound:
            print("Please launch docker container %s" % self.name)
            sys.exit(1)

    def _step(self, action):
        self.steps += 1
        self._take_action(action)
        has_collided = self.client.getCollisionInfo()[0]
        reward = default_reward if has_collided else 0
        ob = self._get_state()
        return ob, reward, has_collided, {}

    def _take_action(self, action):
        direction = Directions[action]
        try:
            # TODO Move by angle
            # self.client.moveByAngle(self, pitch, roll, z, yaw, duration):
            print("self.client.moveByAngle(1, 0, 2.5, %s, 10)" % direction)
            self.client.moveByAngle(1, 0, 2.5, direction, 10)
            # self.client.moveByVelocity(2, 0, 0, 10, DrivetrainType.ForwardOnly, YawMode(False, direction))
        except Exception as e:
                    print("Container %s: Moving by %s returned error %s" % (self.name, direction, e))

    def _get_state(self, raw=False):
        try:
            # rawImage = self.client.getImageForCamera(0, AirSimImageType.Scene)
            # if (rawImage is None):
            #     print("Camera is not returning image, please check airsim for error messages")
            #     sys.exit(0)
            # frame = cv2.imdecode(rawImage, cv2.IMREAD_GRAYSCALE)
            self.vnc.captureScreen('%d.png' % self.container_id)
            frame = cv2.imread('%d.png' % self.container_id, cv2.IMREAD_GRAYSCALE)
        except Exception as e:
            print("Image retrieval and decode failed with error %s" % e)
            sys.exit(1)
        if raw:
            return frame
        print("Shape is %s" % frame.shape)

        # TODO make the frame size inside airsim
        frame = frame[0:500,0:500]
        frame = cv2.resize(frame, (80, 80))
        frame = cv2.resize(frame, (42, 42))
        frame = frame.astype(np.float32)
        frame *= (1.0 / 255.0)
        frame = np.reshape(frame, [42, 42, 1])
        return frame

    def _reset(self):
        self.container.restart(timeout=0)
        armed = False
        tries = 0
        while not armed and tries < 5:
            sleep(1)
            print("Container %s: Trying to arm after $s tries" % (self.name, tries))
            try: 
                self.client = PythonClient(rpcport=self.rpcport)
                armed = self.client.arm()
                if armed:
                    self.client.takeoff()
            except Exception as e:
                print("Container %s: Arming returned error %s" % (self.name, e))
            tries += 1
        if not armed:
            print("Container %s: Failed to Arm. Exiting.." % self.name)
            sys.exit(1)
        print("Container %s: Armed" % self.name)

        self.vnc = vncapi.connect('localhost::590%d' % self.container_id, password=None)

    def _render(self, mode='human', close=False):
        return self._get_state(raw=True)
