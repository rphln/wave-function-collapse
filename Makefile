format: autoflake isort black

autoflake:
	autoflake --in-place --remove-all-unused-imports --recursive $(CURDIR)

isort:
	isort $(CURDIR)

black:
	black --target-version py310 $(CURDIR)

.PHONY: format autoflake isort black
