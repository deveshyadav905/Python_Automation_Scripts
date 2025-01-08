import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import json
import logging
from typing import List, Dict
from atlassian import Bitbucket
from crawlers.settings import BITBUCKET_CONFIG


class BitbucketAutomation:
    def __init__(self):
        self.bitbucket = Bitbucket(
            url=BITBUCKET_CONFIG["bitbucket_url"],
            username=BITBUCKET_CONFIG["username"],
            password=BITBUCKET_CONFIG["password"],
            cloud=True
        )
        self.project_key = BITBUCKET_CONFIG["project_key"]
        self.target_branch = BITBUCKET_CONFIG["target_branch"]  # Target branch (e.g., 'main')``
        self.source_branches = BITBUCKET_CONFIG["source_branches"]  # List of source branches
        self.repo_slug = BITBUCKET_CONFIG["repo_slug"]  # Repository slug
        self.setup_logging()

    def setup_logging(self):
        """Configure logging to write all logs to a single file."""
        log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # Single log file handler
        file_handler = logging.FileHandler("bitbucket_combined.log")
        file_handler.setFormatter(log_formatter)

        # Console log handler (optional for real-time debugging)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)

        # Get the root logger and attach handlers
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)  # Capture all levels of logs
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        self.logger = root_logger

    def create_pull_request(self, source_branch: str) -> Dict:
        """Create a pull request from source_branch to target_branch in the repo_slug."""
        try:
            data = {
                "title": f"Merge {source_branch} into {self.target_branch}",
                "description": f"Automated PR created for merging {source_branch} into {self.target_branch}",
                "source": {"branch": {"name": source_branch}},
                "destination": {"branch": {"name": self.target_branch}},
                "close_source_branch": False,
            }

            pr = self.bitbucket.create_pull_request(
                repository_slug=self.repo_slug,
                project_key=self.project_key,
                data=data,
            )
            self.logger.info(f"Pull request created for {source_branch} to {self.target_branch}.")
            return pr
        except Exception as e:
            self.logger.error(
                f"Failed to create pull request for branch {source_branch}: {str(e)}"
            )
            return {}

    # def check_merge_conflicts(self, pr_id: int) -> bool:
    #     """Check if the pull request has merge conflicts using the Bitbucket API."""
    #     try:
    #         # Use is_pull_request_can_be_merged method
    #         can_merge = self.bitbucket.is_pull_request_can_be_merged(
    #             project_key=self.project_key,
    #             repository_slug=self.repo_slug,
    #             pr_id=pr_id,
    #         )
    #         if can_merge:
    #             self.logger.info(f"Pull request {pr_id} can be merged. No conflicts detected.")
    #             return False  # No conflicts
    #         else:
    #             self.logger.warning(f"Pull request {pr_id} cannot be merged. Conflicts detected.")
    #             return True  # Conflicts detected
    #     except Exception as e:
    #         self.logger.error(f"Error checking merge conflicts for PR {pr_id}: {str(e)}")
    #         return True  # Default to conflicts in case of error
    
    def merge_pull_request(self, pr_id: int) -> bool:
        """Merge a pull request and check for merge conflicts."""
        try:
            merge_message = f"Merging pull request {pr_id} into {self.target_branch}"
            response = self.bitbucket.merge_pull_request(
                project_key=self.project_key,
                repository_slug=self.repo_slug,
                pr_id=pr_id,
                merge_message=merge_message,
                merge_strategy="merge_commit",  # You can adjust this as needed
            )

            if response.get("state") == "MERGED":
                self.logger.info(f"Pull request {pr_id} successfully merged.")
                return True
            else:
                self.logger.error(f"Failed to merge PR {pr_id}. State: {response.get('state')}")
                return False
        except Exception as e:
            # Check if the exception message is a JSON error from Bitbucket
            response = e.response
            if response.status_code:
                self.logger.error(f"Merge conflict occurred for PR {pr_id}: {response.text}. Status code: {response.status_code}")
            return False


    def decline_pull_request(self, pr_id: int):
        """Decline a pull request."""
        try:
            # bitbucket.get_pull_requests_activities(project, repository, pull_request_id)

            pr_details = self.bitbucket.get_pull_request(self.project_key, self.repo_slug,pr_id)

            self.bitbucket.decline_pull_request(
                project_key=self.project_key,
                repository_slug=self.repo_slug,
                pr_id=pr_id,
                pr_version=pr_id
                
            )
            self.logger.info(f"Pull request {pr_id} has been declined.")
        except Exception as e:
            self.logger.error(f"Error declining PR {pr_id}: {str(e)}")

    def process_branch(self, source_branch: str) -> bool:
        """Process a single branch to create and merge a pull request."""
        self.logger.info(f"Processing branch: {source_branch}")

        # Create pull request
        pr = self.create_pull_request(source_branch)
        if not pr:
            self.logger.error(f"Failed to create pull request for branch {source_branch}.")
            return False

        pr_id = pr.get("id")
        if not pr_id:
            self.logger.error(f"Invalid pull request response for branch {source_branch}.")
            return False

        # Check merge conflicts
        # if not self.check_merge_conflicts(pr_id):
        if self.merge_pull_request(pr_id):
            return True
        else:
            self.logger.warning(f"Conflicts detected for branch {source_branch}. Declining PR {pr_id}.")
            self.decline_pull_request(pr_id)

        return False

    def run_automation(self):
        """Main automation process."""
        self.logger.info("Starting Bitbucket automation process.")
        successful_merges = []
        failed_merges = []

        for source_branch in self.source_branches:
            if self.process_branch(source_branch):
                successful_merges.append(source_branch)
                self.logger.info(f"Successfully merged branch {source_branch}.")
            else:
                failed_merges.append(source_branch)
                self.logger.warning(f"Failed to merge branch {source_branch}.")

        # Print summary
        self.logger.info(f"Successfully merged: {successful_merges}")
        self.logger.info(f"Failed to merge: {failed_merges}")

        return successful_merges, failed_merges


def main():
    automation = BitbucketAutomation()
    automation.run_automation()


if __name__ == "__main__":  
    main()
