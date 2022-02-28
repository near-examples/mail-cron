import github.Repository
import structlog
from github import Github
from unsync import unsync

from classes import Credentials, RepoSuccess, Configuration
from helpers import (
    get_repo_new_workflow_run_success,
    get_repo_latest_completed_workflow_run,
)
from mail import send_email


logger = structlog.get_logger()


@unsync
def run_repo_tests(repo: github.Repository.Repository):
    logger.info(f"Running tests for repository: {repo}")
    latest_test_run = get_repo_latest_completed_workflow_run(repo)
    repo.create_repository_dispatch(
        Configuration.repository_dispatch_type, client_payload={}
    )
    repo_success = get_repo_new_workflow_run_success(latest_test_run, repo)
    return repo_success


def check_repositories_tests(github_client: Github, github_accounts):
    logger.info(f"Calling tests to check for failures (accounts={github_accounts})")
    results = []
    for account in github_accounts:
        repos = github_client.get_user(account).get_repos()
        devrel_repo_tasks = [run_repo_tests(repo) for repo in repos]
        account_results: list[RepoSuccess] = [
            task.result() for task in devrel_repo_tasks
        ]
        results.extend(account_results)
    return results


def run_tutorials_testing_report(to_address: str, github_accounts: list[str]):
    github_client = Github(Credentials.github_token)
    repos_test_results = check_repositories_tests(github_client, github_accounts)
    failed_test_repos = [r for r in repos_test_results if not r.success]
    if failed_test_repos:
        subject = "‼️ Failing Tests Found in GitHub Repositories ‼️"
        body = "--- Failed ---\n"
        body += "\n" + ",\n".join(str(rs) for rs in failed_test_repos)
        body += "\n\n--- Success ---\n"
        body += "\n" + ",\n".join(str(rs) for rs in repos_test_results if rs.success)
        send_email(
            Credentials.email_user,
            Credentials.email_password,
            to_address,
            subject,
            body,
        )
        return
    logger.info(f"No failing repos found 👍")


if __name__ == "__main__":
    run_tutorials_testing_report(
        to_address=Credentials.email_user, github_accounts=Configuration.github_accounts
    )
