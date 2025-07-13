# Improvements

## Process

- Select the first Todo Item
- Implement it
- Fix errors until `make lint` succeeds
- Fix errors until `pulumi preview` succeeds
- Update this file to reflect the finished Todo item
- Create a semantic commit in this repo

## Todo Items

- [ ] refactor __main__.py to use a more maintainable configuration pattern
- [ ] fix FIXME items in chime/chime.py (populate command and local.Command issues)
- [ ] add ruff configuration to pyproject.toml and remove pylint suppressions
- [ ] create a common base class for all ComponentResources to reduce duplication
- [ ] add proper error handling and validation to config loading
- [ ] implement proper logging throughout the codebase
- [ ] add integration tests for ComponentResources
- [ ] create a proper CI/CD pipeline configuration
- [ ] add resource tagging and cost tracking
- [ ] implement proper secret management strategy

## Completed Items

- [x] add docstrings everywhere
- [x] convert all app()s to ComponentResources. Name things like Foo and foo, not FooComponent and foo_component
- [x] fix all mypy errors
- [x] convert all pulumi config usage to pydantic model usage
- [x] alphabetize all imports
- [x] remove app() functions and instantiate ComponentResources directly 