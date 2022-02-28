import time

import github.Repository

from classes import RepoSuccess, Configuration


def get_repo_new_workflow_run_success(latest_test_run, repo):
    newest_test_run = get_repo_latest_complete_workflow_run(repo)
    counter, repo_success = 0, None
    while (
        newest_test_run is None
        or newest_test_run.created_at <= latest_test_run.created_at
    ):
        counter += 1
        time.sleep(Configuration.new_workflow_run_wait_seconds)
        newest_test_run = get_repo_latest_complete_workflow_run(repo)
        if counter >= Configuration.new_workflow_run_wait_attempts:
            repo_success = RepoSuccess(
                name=repo.full_name,
                success=False,
                html_url=repo.html_url
                if not newest_test_run
                else newest_test_run.html_url,
                message="No new tests could be triggered as a result of this script",
            )
            break

    if repo_success is None:
        wait_count, message = 0, None
        while newest_test_run.status != "completed":
            wait_count += 1
            time.sleep(Configuration.repo_actions_completion_try_wait_seconds)
            if wait_count >= Configuration.repo_actions_completion_wait_count_limit:
                message = (
                    f"Timed out. Waited longer than "
                    f"{wait_count*Configuration.repo_actions_completion_try_wait_seconds}s "
                    f"for repo action to complete."
                )
                break
        success = newest_test_run.conclusion == "success"
        repo_success = RepoSuccess(
            name=repo.full_name,
            success=success,
            html_url=newest_test_run.html_url,
            message=message,
        )

    return repo_success


def get_repo_latest_complete_workflow_run(
    repo: github.Repository.Repository,
) -> None or github.WorkflowRun.WorkflowRun:
    for run in repo.get_workflow_runs():
        if run.status == "completed":
            return run
    return None
