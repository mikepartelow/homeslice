from flytekit import task, workflow  # type: ignore


@task  # (requests=Resources(cpu="900m", mem="3Gi"))
def say_hello() -> str:
    return "hello world"


@workflow
def my_wf() -> str:
    res = say_hello()
    return res


if __name__ == "__main__":
    print(f"Running my_wf() {my_wf()}")
