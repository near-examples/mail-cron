import github.Repository
import structlog
from github import Github
from unsync import unsync

from classes import Credentials, RepoSuccess, Configuration, SuccessType
from helpers import (
    get_repo_new_workflow_run_success,
    get_repo_latest_workflow_run,
)
from mail import send_email, get_mail_body_and_subject


logger = structlog.get_logger()


@unsync
def run_repo_tests(repo: github.Repository.Repository):
    logger.info(f"Running tests for repository: {repo}")
    previous_test_run = get_repo_latest_workflow_run(repo)
    repo.create_repository_dispatch(
        Configuration.repository_dispatch_type, client_payload={}
    )
    repo_success = get_repo_new_workflow_run_success(previous_test_run, repo)
    logger.debug(f"Tests complete for: {repo}")
    return repo_success


def check_repositories_tests(github_client: Github, github_accounts):
    logger.info(f"Calling tests to check for failures (accounts={github_accounts})")
    results = []
    for account in github_accounts:
        repos = [
            r
            for r in github_client.get_user(account).get_repos()
            if r.name in Configuration.include_repos
        ]
        devrel_repo_tasks = [run_repo_tests(repo) for repo in repos]
        account_results: list[RepoSuccess] = [
            task.result() for task in devrel_repo_tasks
        ]
        results.extend(account_results)
    return results


def run_tutorials_testing_report(to_address: str, github_accounts: list[str]):
    github_client = Github(Credentials.github_token)
    repos_test_results = check_repositories_tests(github_client, github_accounts)
    not_passed_test_repos = [
        r for r in repos_test_results if r.success_type != SuccessType.PASSED
    ]
    if not_passed_test_repos:
        body, subject = get_mail_body_and_subject(repos_test_results)
        send_email(
            from_address=Configuration.from_address,
            login_address=Credentials.email_user,
            login_password=Credentials.email_password,
            to_address=to_address,
            subject=subject,
            body=body,
        )
        return
    logger.info(f"No failing repos found 👍")


if __name__ == "__main__":
    run_tutorials_testing_report(
        to_address=Configuration.to_address,
        github_accounts=Configuration.github_accounts,
    )
