## How to run this bot?

This bot has 4 services. The following area the services:
1. Rasa framework
``nohup rasa run --enable-api --cors "*" > rasa.log 2>&1 &``
2. Rasa action
``nohup rasa run actions > actions.log 2>&1 &``
3. Chatbot
``nohup python3 main.py > app.log 2>&1 &``
4. Worker run behind the scene
``nohup celery -A tasks worker --loglevel=INFO > tasks.log &``