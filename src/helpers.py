import datetime
import time

import github.Repository
from github import Github
from github.WorkflowRun import WorkflowRun

from classes import RepoSuccess, Configuration, SuccessType, Credentials


def get_repo_new_workflow_run_success(previous_test_run: WorkflowRun | None, repo):
    newest_test_runs, repo_success = get_triggered_repo_workflow_runs(
        repo, previous_test_run
    )

    if repo_success is None:
        repo_success = get_repo_workflows_conclusions(repo, newest_test_runs)

    return repo_success


def get_repo_workflows_conclusions(
    repo: github.Repository.Repository,
    newest_test_runs: list[github.WorkflowRun.WorkflowRun],
):
    run_id_results: dict[int, list] = {run.id: [] for run in newest_test_runs}
    time.sleep(Configuration.new_completed_run_wait_seconds)
    for run_id in run_id_results.keys():
        attempt_count, message = 1, None
        run = repo.get_workflow_run(run_id)
        while run.status != "completed":
            attempt_count += 1
            if attempt_count > Configuration.new_completed_run_wait_attempts:
                message = (
                    f"Test run for repo exceeds limit time of "
                    f"{Configuration.new_completed_run_wait_seconds * Configuration.new_completed_run_wait_attempts}"
                )
                run_id_results[run_id].extend([False, message])
                break
            time.sleep(Configuration.new_completed_run_wait_seconds)
            run = repo.get_workflow_run(run_id)
        else:
            run_success = run.conclusion == "success"
            message = (
                None if run_success else f"❗ Tests have failed ❗ See: {run.html_url}"
            )
            run_id_results[run_id].extend([run_success, message])

    success = min([r[0] for r in run_id_results.values()])
    message = str(run_id_results)
    repo_success = RepoSuccess(
        name=repo.full_name,
        success_type=SuccessType.PASSED if success else SuccessType.FAILED,
        html_url=repo.html_url,
        message=message if not success else None,
    )
    return repo_success


def get_triggered_repo_workflow_runs(
    repo: github.Repository.Repository,
    previous_test_run: github.WorkflowRun.WorkflowRun,
) -> tuple[list[github.WorkflowRun.WorkflowRun], None | RepoSuccess]:
    repo_success = None
    time.sleep(Configuration.new_created_run_wait_seconds)
    newest_test_runs = get_repo_newest_workflow_runs(repo, previous_test_run)

    if not newest_test_runs:
        repo_success = RepoSuccess(
            name=repo.full_name,
            success_type=SuccessType.UNTESTED,
            html_url=repo.html_url,
            message="No new tests could be triggered as a result of this script",
        )

    return newest_test_runs, repo_success


def is_new_test_run(previous_test_run, newest_test_run):
    if previous_test_run and newest_test_run:
        return previous_test_run.created_at < newest_test_run.created_at
    if not previous_test_run:
        return newest_test_run is not None
    return False


def get_repo_latest_workflow_run(
    repo: github.Repository.Repository,
) -> None or github.WorkflowRun.WorkflowRun:
    for run in repo.get_workflow_runs():
        return run
    return None


def get_repo_newest_workflow_runs(
    repo: github.Repository.Repository, past_run: github.WorkflowRun.WorkflowRun
) -> list[github.WorkflowRun.WorkflowRun]:
    time_in_past = datetime.datetime.now() - datetime.timedelta(days=1)
    prev_run_datetime = time_in_past if not past_run else past_run.created_at
    return [
        run for run in repo.get_workflow_runs() if run.created_at > prev_run_datetime
    ]


def is_tigger_monitoring_window_expired(
    start_time: datetime.datetime, this_time: datetime.datetime
) -> bool:
    elapsed_seconds = (this_time - start_time).seconds
    return (
        True if elapsed_seconds > Configuration.new_created_run_wait_seconds else False
    )


def get_test_run_runtime_seconds(test_run: WorkflowRun | None) -> None | int:
    if not test_run:
        return None
    creation_datetime = test_run.created_at
    update_datetime = test_run.updated_at
    difference_seconds = (creation_datetime - update_datetime).seconds
    if difference_seconds:
        return difference_seconds
    return None


def get_account_repo_list(account: str) -> list[str]:
    github_client = Github(Credentials.github_token)
    github_repos = github_client.get_user(account).get_repos()
    return [r.name for r in github_repos]
