import time

import github.Repository

from classes import RepoSuccess, Configuration


def get_repo_new_workflow_run_success(latest_test_run, repo):
    time.sleep(Configuration.new_complete_workflow_run_wait_seconds)
    newest_test_run = get_repo_latest_completed_workflow_run(repo)
    has_new_test_run = is_new_test_run(latest_test_run, newest_test_run)
    counter, repo_success = 0, None
    while not has_new_test_run:
        counter += 1
        time.sleep(Configuration.new_complete_workflow_run_wait_seconds)
        newest_test_run = get_repo_latest_completed_workflow_run(repo)
        has_new_test_run = is_new_test_run(latest_test_run, newest_test_run)
        if counter >= Configuration.new_complete_workflow_run_wait_attempts:
            repo_success = RepoSuccess(
                name=repo.full_name,
                success=False,
                html_url=newest_test_run.html_url or repo.html_url,
                message="No new tests could be triggered as a result of this script",
            )
            break

    if repo_success is None:
        success = newest_test_run.conclusion == "success"
        repo_success = RepoSuccess(
            name=repo.full_name,
            success=success,
            html_url=newest_test_run.html_url,
        )

    return repo_success


def is_new_test_run(latest_test_run, newest_test_run):
    if latest_test_run and newest_test_run:
        return latest_test_run.created_at < newest_test_run.created_at
    if not latest_test_run:
        return newest_test_run is not None
    return False


def get_repo_latest_completed_workflow_run(
    repo: github.Repository.Repository,
) -> None or github.WorkflowRun.WorkflowRun:
    # noinspection PyArgumentList
    for run in repo.get_workflow_runs(status="completed"):
        return run
    return None
