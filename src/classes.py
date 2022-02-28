import os
from dataclasses import dataclass


@dataclass
class Credentials:
    github_token = os.environ.get("TOKEN")
    email_user = os.environ.get("EMAIL_USERNAME")
    email_password = os.environ.get("EMAIL_PASSWORD")


@dataclass
class Configuration:
    repository_dispatch_type = "tests-report"
    github_accounts = ["idea404"]
    new_created_run_wait_seconds = 10
    new_created_run_wait_attempts = 3
    new_completed_run_wait_seconds = 60
    new_completed_run_wait_attempts = 5


@dataclass
class RepoSuccess:
    name: str
    success: bool
    html_url: str
    message: str = None
