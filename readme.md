Reinforcement Learning with a3c-lstm


This is the airsim branch of my a3c lstm learning code. This code requires Python 3. To install and run this code, first go to the `gym-airsim` directory and type `pip3 install -e .`, which installs the gym environment. Then go to the `a3c-lstm` folder and run the `cmd.sh` script. The script will automatically create a tmux shell for you to observe the progress of your algorithm. Tensorboard will be available at `localhost:12345`.

Note, you must deploy the containerized airsim using the library [here](https://github.com/abhay-agarwal/AirSim)