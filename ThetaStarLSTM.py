
# coding: utf-8

import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
import gym
import gym_astar_transfer
import matplotlib.pyplot as plt


# In[7]:

env = gym.make('AStarTransfer-v0')
states = 100
actions = 4
hidden = 25
# gamma = 0.8 # discount factor


# ### The Policy-Based Agent

# In[3]:

tf.reset_default_graph()

# def discount_rewards(r):
#     """ take 1D float array of rewards and compute discounted reward """
#     discounted_r = np.zeros_like(r)
#     running_add = 0
#     for t in reversed(range(0, r.size)):
#         running_add = running_add * gamma + r[t] 
#         discounted_r[t] = running_add
#     return discounted_r

def process_frame(frame):
    frame = cv2.resize(frame, (80,80))
    frame = cv2.resize(frame, (42,42))
    frame = frame.astype(np.float32)
    frame *= (1.0 / 255.0)
    frame = np.reshape(frame, [42,42,1])

def onehot(s_size, s):
    return np.identity(s_size)[s:s+1]

class agent():
    def __init__(self, lr, s_size,a_size,h_size):
        #These lines established the feed-forward part of the network. The agent takes a state and produces an action.
        self.state_in= tf.placeholder(shape=[None,s_size],dtype=tf.float32)
        hidden = slim.fully_connected(self.state_in,h_size,biases_initializer=None,activation_fn=tf.nn.relu)
        self.output = slim.fully_connected(hidden,a_size,activation_fn=tf.nn.softmax,biases_initializer=None)
        self.chosen_action = tf.argmax(self.output,1)

        #The next six lines establish the training proceedure. We feed the reward and chosen action into the network
        #to compute the loss, and use it to update the network.
        self.reward_holder = tf.placeholder(shape=[None],dtype=tf.float32)
        self.action_holder = tf.placeholder(shape=[None],dtype=tf.int32)
        
        self.indexes = tf.range(0, tf.shape(self.output)[0]) * tf.shape(self.output)[1] + self.action_holder
        self.responsible_outputs = tf.gather(tf.reshape(self.output, [-1]), self.indexes)

        self.loss = -tf.reduce_mean(tf.log(self.responsible_outputs)*self.reward_holder)
        
        tvars = tf.trainable_variables()
        self.gradient_holders = []
        for idx,var in enumerate(tvars):
            placeholder = tf.placeholder(tf.float32,name=str(idx)+'_holder')
            self.gradient_holders.append(placeholder)
        
        self.gradients = tf.gradients(self.loss,tvars)
        
        optimizer = tf.train.AdamOptimizer(learning_rate=lr)
        self.update_batch = optimizer.apply_gradients(zip(self.gradient_holders,tvars))



# In[5]:

myAgent = agent(lr=0.01,s_size=states,a_size=actions,h_size=hidden) #Load the agent.

total_episodes = 1000 #Set total number of episodes to train agent on.
max_ep = 999
update_frequency = 1

init = tf.global_variables_initializer()

try:
    with tf.Session() as sess:
        sess.run(init)
        i = 0
        total_reward = []
        total_length = []
            
        gradBuffer = sess.run(tf.trainable_variables())
        for ix,grad in enumerate(gradBuffer):
            gradBuffer[ix] = grad * 0
            
        while i < total_episodes:
            i += 1
            s = env.reset()
            s = onehot(states, s)
            running_reward = 0
            for j in range(max_ep):
                #env.render()
                a_dist = sess.run(myAgent.output,feed_dict={myAgent.state_in:s})
                a = np.random.choice(a_dist[0],p=a_dist[0])
                a = np.argmax(a_dist == a)
                ob,r,d,_ = env.step(a)
                s1,grid = ob
                s1 = onehot(states, s1)
                episode = np.array([[s,a,r,s1]])
                running_reward += r
                s = s1

                feed_dict={myAgent.reward_holder:episode[:,2],
                        myAgent.action_holder:episode[:,1],myAgent.state_in:np.vstack(episode[:,0])}
                grads = sess.run(myAgent.gradients, feed_dict=feed_dict)

                for idx,grad in enumerate(grads):
                    gradBuffer[idx] += grad

                if i % update_frequency == 0:
                    feed_dict= dictionary = dict(zip(myAgent.gradient_holders, gradBuffer))
                    _ = sess.run(myAgent.update_batch, feed_dict=feed_dict)
                    for ix,grad in enumerate(gradBuffer):
                        gradBuffer[ix] = grad * 0

                if d == True:
                    total_reward.append(running_reward)
                    total_length.append(j)
                    break

except KeyboardInterrupt:
    pass
finally:
    env.render(close=True)


# In[6]:
plt.figure(1)
plt.subplot(211)
plt.plot(total_reward)
plt.subplot(212)
plt.plot(total_length)
plt.show()

# In[7]:




