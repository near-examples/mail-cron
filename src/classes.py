import os
from dataclasses import dataclass


@dataclass
class Credentials:
    github_token = os.environ.get("TOKEN")
    email_user = os.environ.get("EMAIL_USERNAME")
    email_password = os.environ.get("EMAIL_PASSWORD")


@dataclass
class Configuration:
    github_accounts = ["idea404"]
    new_workflow_run_wait_seconds = 4
    new_workflow_run_wait_attempts = 3
    repo_actions_completion_try_wait_seconds = 5
    repo_actions_completion_wait_count_limit = 200


@dataclass
class RepoSuccess:
    name: str
    success: bool
    html_url: str
    message: str = None
