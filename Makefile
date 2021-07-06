
local-run:
	source env.sh && python local.py

lint:
	flake8 api > flake8-results.txt api || true
	echo '============================================================' >> flake8-results.txt
	flake8 test >> flake8-results.txt test  || true

build-lambda:
	ls
	echo 'Build Lambda zip for python'

acceptance-tests:
	pytest
