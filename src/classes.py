import os
from dataclasses import dataclass

from variables import EXCLUDE_REPOS


@dataclass
class Credentials:
    github_token = os.environ.get("TOKEN")
    email_user = os.environ.get("EMAIL_USERNAME")
    email_password = os.environ.get("EMAIL_PASSWORD")


@dataclass
class Configuration:
    exclude_repos = EXCLUDE_REPOS
    repository_dispatch_type = "tests-report"
    github_accounts = ["near-examples"]
    to_address = "devrel-ops@near.org"
    from_address = "devrel-ops@near.org"
    new_created_run_wait_seconds = 40
    new_completed_run_wait_seconds = 60
    new_completed_run_wait_attempts = 60


@dataclass
class SuccessType:
    PASSED = "PASSED"
    UNTESTED = "UNTESTED"
    FAILED = "FAILED"


@dataclass
class RepoSuccess:
    name: str
    success_type: SuccessType
    html_url: str
    message: str = None
