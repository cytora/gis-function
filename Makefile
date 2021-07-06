
local-run:
	source env.sh && python local.py

lint:
	flake8 api > flake8-results.txt api || true
	echo '============================================================' >> flake8-results.txt
	flake8 test >> flake8-results.txt test  || true

build-lambda:
	ls -la
	pwd
	echo 'Build Lambda zip for python with dependencies starting ...'
	cd app/
	# zip -r ../dist.zip .
	echo 'Build Lambda zip for python with dependencies complete.'
	ls -la
	pwd

acceptance-tests:
	pytest
