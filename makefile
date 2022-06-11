
HADOLINT:=docker run --rm -v "$(PWD):$(PWD)" -w="$(PWD)" --entrypoint hadolint hadolint/hadolint

TEST_TARGETS:=test_pylint test_hadolint


test: $(TEST_TARGETS)
	@echo Testing done

test_pylint: src/teslamte_telegram_bot.py
	docker run --rm -v "$(PWD):$(PWD)" -it $$(docker build -q .) pylint --persistent=n $^

test_hadolint: Dockerfile
	${HADOLINT} $^




