APP_NAME = drbl_manage
APP_AUTHOR = vaclav-v

FILE_VSCODE_SETTINGS = .vscode/settings.json
FILE_LINT_SETTINGS = setup.cfg

define VSCODE_SETTINGS
echo "{" >> $(FILE_VSCODE_SETTINGS)
echo "\"python.pythonPath\": \"`poetry show -v 2 | grep virtualenv | cut -d ' ' -f 3 | xargs` \"," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.linting.pylintEnabled\": false," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.linting.flake8Enabled\": true," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.linting.mypyEnabled\": true," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.linting.enabled\": true," >> $(FILE_VSCODE_SETTINGS)
echo "}" >> $(FILE_VSCODE_SETTINGS)

endef


FILE_GITIGNORE = .gitignore

define GITIGNORE
echo ".venv" >> $(FILE_GITIGNORE)
echo ".vscode" >> $(FILE_GITIGNORE)
echo "*_cache" >> $(FILE_GITIGNORE)
echo "__pycache__" >> $(FILE_GITIGNORE)
echo ".python-version" >> $(FILE_GITIGNORE)
echo "${FILE_LINT_SETTINGS}" >> $(FILE_GITIGNORE)

endef

define FLAKE8_SETTINGS
echo "[flake8]" >> $(FILE_LINT_SETTINGS)
echo "    max-line-length = 100" >> $(FILE_LINT_SETTINGS)

endef

define MYPY_SETTINGS
echo "[mypy]" >> $(FILE_LINT_SETTINGS)
echo "    plugins = sqlmypy" >> $(FILE_LINT_SETTINGS)

endef


init:
	poetry init -n --name $(APP_NAME) --author $(APP_AUTHOR)
	poetry add --dev flake8
	poetry add --dev mypy
	mkdir .vscode
	touch $(FILE_VSCODE_SETTINGS)
	$(VSCODE_SETTINGS)
	touch $(FILE_GITIGNORE)
	$(GITIGNORE)
	touch $(FILE_LINT_SETTINGS)
	$(FLAKE8_SETTINGS)
	mkdir $(APP_NAME)
	touch $(APP_NAME)/__init__.py
	echo '"""Main module $(APP_NAME) project."""' > $(APP_NAME)/__init__.py
	poetry shell

lint:
	poetry run flake8 $(APP_NAME)
	poetry run mypy $(APP_NAME)

install:
	poetry install

sqlalchemy:
	poetry add sqlalchemy
	poetry add psycopg2-binary
	poetry add alembic
	poetry run alembic init alembic
	$(MYPY_SETTINGS)

db_revision:
	poetry run alembic revision --autogenerate

db_update:
	poetry run alembic upgrade head

test_db:
	docker run --name test-postgres -e POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_DB=postgres -d -p 5432:5432 postgres

req:
	poetry export -f requirements.txt --output requirements.txt --without-hashes