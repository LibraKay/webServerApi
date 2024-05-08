ps -aux | grep python3|xargs kill -9
nohup python3 manage.py runserver 0.0.0.0:8000 >djserverlog.out 2>&1 &

