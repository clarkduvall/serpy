LINT_TARGETS=benchmarks docs/ serpy/ setup.py tests/

lint:
	@flake8 $(LINT_TARGETS) && echo "flake8: OK"
	@pyflakes $(LINT_TARGETS) && echo "pyflakes: OK"
	@pep8 --statistics --count $(LINT_TARGETS) && echo "pep8: OK"

.PHONY: lint
