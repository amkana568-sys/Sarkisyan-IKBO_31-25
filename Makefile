.PHONY: test example

test:
	python -m unittest discover -s tests -v

example:
	python src/main.py --output result.json < examples/computer.cfg
