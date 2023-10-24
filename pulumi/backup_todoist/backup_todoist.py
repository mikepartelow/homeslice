import pulumi
import pulumi_kubernetes as kubernetes
import homeslice
from secrets import backup_todoist

NAME = "backup-todoist"

def app(namespace: str, config: pulumi.Config) -> None:
    image = config["image"]
    private_key_path = config["private_key_path"]
    author_name = config["author_name"]
    author_email = config["author_email"]

    metadata=homeslice.metadata(NAME, namespace)

    configmap = kubernetes.core.v1.ConfigMap(
        NAME,
        metadata=metadata,
        data=dict(
            TODOIST_BACKUP_GIT_CLONE_URL=backup_todoist.SECRETS["TODOIST_BACKUP_GIT_CLONE_URL"],
            TODOIST_BACKUP_TODOIST_TOKEN=backup_todoist.SECRETS["TODOIST_BACKUP_TODOIST_TOKEN"],
            TODOIST_BACKUP_PRIVATE_KEY_PATH=private_key_path,
            TODOIST_BACKUP_AUTHOR_NAME=author_name,
            TODOIST_BACKUP_AUTHOR_EMAIL=author_email,
        )
    )

    env_from = [
        kubernetes.core.v1.EnvFromSourceArgs(
            config_map_ref=kubernetes.core.v1.ConfigMapEnvSourceArgs(
                name=configmap.metadata.name,
            )
        )
    ]

    cronjob = kubernetes.batch.v1.CronJob(
        NAME,
        metadata=metadata,
        spec=kubernetes.batch.v1.CronJobArgs(
            spec=kubernetes.batch.v1.CronJobSpecArgs(
                schedule="1 */1 * * *",  # Schedule the job to run every hour
                job_template=kubernetes.batch.v1.JobTemplateSpec(
                    spec=kubernetes.batch.v1.JobSpec(
                        template=kubernetes.core.v1.PodTemplateSpec(
                            spec=kubernetes.core.v1.PodSpec(
                                containers=[
                                    kubernetes.core.v1.Container(
                                        name=NAME,
                                        image=image,
                                    )
                                ],
                                restart_policy="Never", # FIXME: ?
                            ),
                        ),
                    ),
                ),
            )
        )
    )

    # these are here just so we don't get unused variable warnings
    pulumi.export("backupTodoistCronjob", cronjob)
