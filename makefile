
HADOLINT:=docker run --rm -v "$(PWD):$(PWD)" -w="$(PWD)" --entrypoint hadolint hadolint/hadolint

TEST_TARGETS:=test_pylint test_hadolint test_black test_isort
PY_SRC:=src/teslmate_telegram_bot.py


test: $(TEST_TARGETS)
	@echo Testing done

test_pylint: $(PY_SRC)
	docker run --rm -v "$(PWD):$(PWD)" -it $$(docker build -q .) pylint --persistent=n $^

test_black: $(PY_SRC)
	black --check $^

test_isort: $(PY_SRC)
	isort --check $^

format: $(PY_SRC)
	isort $^
	black $^

test_hadolint: Dockerfile
	${HADOLINT} $^
