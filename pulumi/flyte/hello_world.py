from flytekit import task, workflow  # type: ignore


@task  # type: ignore  # (requests=Resources(cpu="900m", mem="3Gi"))
def say_hello() -> str:
    """Return a simple hello world message."""
    return "hello world"


@workflow  # type: ignore
def my_wf() -> str:
    """Execute the hello world workflow.
    
    Returns the result of the say_hello task.
    """
    res = say_hello()
    return res  # type: ignore


if __name__ == "__main__":
    print(f"Running my_wf() {my_wf()}")
