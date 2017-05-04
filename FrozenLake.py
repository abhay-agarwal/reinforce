
# coding: utf-8

# In[1]:

import gym
import numpy as np
import random
import tensorflow as tf
import matplotlib.pyplot as plt


# In[2]:

env = gym.make('FrozenLake8x8-v0')
states = 64
actions = 4


# In[3]:

tf.reset_default_graph()


# In[4]:

#These lines establish the feed-forward part of the network used to choose actions
inputs1 = tf.placeholder(shape=[1,states],dtype=tf.float32)
W = tf.Variable(tf.random_uniform([states,actions],0,0.01))
Qout = tf.matmul(inputs1,W)
predict = tf.argmax(Qout,1)

#Below we obtain the loss by taking the sum of squares difference between the target and prediction Q values.
nextQ = tf.placeholder(shape=[1,actions],dtype=tf.float32)
loss = tf.reduce_sum(tf.square(nextQ - Qout))
trainer = tf.train.GradientDescentOptimizer(learning_rate=0.1)
updateModel = trainer.minimize(loss)


# In[5]:

init = tf.initialize_all_variables()

# Set learning parameters
y = .99
e = 0.1
num_episodes = 1000
#create lists to contain total rewards and steps per episode
jList = []
rList = []
try:
    with tf.Session() as sess:
        sess.run(init)
        for i in range(num_episodes):
            #Reset environment and get first new observation
            s = env.reset()
            rAll = 0
            d = False
            j = 0
            #The Q-Network
            while j < 99:
                env.render()
                j+=1
                #Choose an action by greedily (with e chance of random action) from the Q-network
                a,allQ = sess.run([predict,Qout],feed_dict={inputs1:np.identity(states)[s:s+1]})
                if np.random.rand(1) < e:
                    a[0] = env.action_space.sample()
                #Get new state and reward from environment
                s1,r,d,_ = env.step(a[0])
                #Obtain the Q' values by feeding the new state through our network
                Q1 = sess.run(Qout,feed_dict={inputs1:np.identity(states)[s1:s1+1]})
                #Obtain maxQ' and set our target value for chosen action.
                maxQ1 = np.max(Q1)
                targetQ = allQ
                targetQ[0,a[0]] = r + y*maxQ1
                #Train our network using target and predicted Q values
                _,W1 = sess.run([updateModel,W],feed_dict={inputs1:np.identity(states)[s:s+1],nextQ:targetQ})
                rAll += r
                s = s1
                if d == True:
                    #Reduce chance of random action as we train the model.
                    e = 1./((i/50) + 10)
                    break
            jList.append(j)
            rList.append(rAll)
except KeyboardInterrupt:
    pass
finally:
    env.render(close=True)
    print("Percent of succesful episodes: " + str(sum(rList)/num_episodes) + "%")


# In[6]:
plt.figure(1)
plt.subplot(211)
plt.plot(rList)
plt.subplot(212)
plt.plot(jList)
plt.show()

# In[7]:




# In[ ]:




# In[ ]:



