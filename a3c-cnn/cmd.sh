kill $( lsof -i:12345 -t ) > /dev/null 2>&1
kill $( lsof -i:12222-12224 -t ) > /dev/null 2>&1
tmux kill-session -t a3c
tmux new-session -s a3c -n ps -d bash
tmux new-window -t a3c -n tb bash
tmux new-window -t a3c -n http bash
tmux new-window -t a3c -n htop bash
sleep 1
tmux send-keys -t a3c:ps 'python3 train.py --eval_every 60 --model_dir ./logs ' Enter
tmux send-keys -t a3c:tb 'tensorboard --logdir ./logs --port 12345' Enter
tmux send-keys -t a3c:http 'python3 -m http.server 12346' Enter
tmux send-keys -t a3c:htop htop Enter
tmux attach -t a3c