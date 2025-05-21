install:
	pip install -r requirements.txt

run:
	python bot.py

test:
	pytest test_bot.py

all: install test run