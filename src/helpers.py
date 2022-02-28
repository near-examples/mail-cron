import time

import github.Repository
from github.WorkflowRun import WorkflowRun

from classes import RepoSuccess, Configuration


def get_repo_new_workflow_run_success(previous_test_run: WorkflowRun | None, repo):
    time.sleep(Configuration.new_created_run_wait_seconds)
    newest_test_run = get_repo_latest_workflow_run(repo)
    counter, repo_success = 0, None
    while not is_new_test_run(previous_test_run, newest_test_run):
        counter += 1
        if counter >= Configuration.new_created_run_wait_attempts:
            repo_success = RepoSuccess(
                name=repo.full_name,
                success=False,
                html_url=newest_test_run.html_url if newest_test_run else repo.html_url,
                message="No new tests could be triggered as a result of this script",
            )
            break
        time.sleep(Configuration.new_created_run_wait_seconds)
        newest_test_run = get_repo_latest_workflow_run(repo)

    if repo_success is None:
        attempt_count, message = 0, None
        while newest_test_run.status != "completed":
            attempt_count += 1
            if attempt_count > Configuration.new_completed_run_wait_attempts:
                message = (
                    f"Test run for repo exceeds limit time of "
                    f"{Configuration.new_completed_run_wait_seconds*Configuration.new_completed_run_wait_attempts}"
                )
                break
            time.sleep(Configuration.new_completed_run_wait_seconds)
            newest_test_run = get_repo_latest_workflow_run(repo)

        success = newest_test_run.conclusion == "success"
        repo_success = RepoSuccess(
            name=repo.full_name,
            success=success,
            html_url=newest_test_run.html_url,
            message=message,
        )

    return repo_success


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


def get_test_run_runtime_seconds(test_run: WorkflowRun | None) -> None | int:
    if not test_run:
        return None
    creation_datetime = test_run.created_at
    update_datetime = test_run.updated_at
    difference_seconds = (creation_datetime - update_datetime).seconds
    if difference_seconds:
        return difference_seconds
    return None
