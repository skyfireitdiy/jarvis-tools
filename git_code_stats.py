# -*- coding: utf-8 -*-
import os
import subprocess
import tempfile
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Dict, Any
from jarvis.jarvis_utils.output import PrettyOutput, OutputType

class git_code_stats:
    name = "git_code_stats"
    description = "Analyzes a Git repository to calculate lines of code (LOC) over a specified period on a monthly basis, using 'loc' as the statistics tool."
    parameters = {
        "type": "object",
        "properties": {
            "start_date": {
                "type": "string",
                "description": "The start date for the analysis in YYYY-MM-DD format."
            },
            "end_date": {
                "type": "string",
                "description": "The end date for the analysis in YYYY-MM-DD format."
            },
            "repo_path": {
                "type": "string",
                "description": "Path to the local Git repository.",
                "default": "."
            },
            "file_types": {
                "type": "string",
                "description": "Comma-separated list of file extensions to analyze (e.g., 'rs,py,go')."
            }
        },
        "required": ["start_date", "end_date", "file_types"]
    }

    @staticmethod
    def check() -> bool:
        """Checks if git and loc are installed."""
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
            subprocess.run(["loc", "--version"], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            PrettyOutput.print("Error: 'git' and 'loc' command-line tools are required.", OutputType.ERROR)
            return False

    def _run_command(self, command, cwd):
        return subprocess.run(command, check=True, capture_output=True, text=True, cwd=cwd)

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        start_date_str = args["start_date"]
        end_date_str = args["end_date"]
        repo_path = args.get("repo_path", ".")
        file_types = args["file_types"]

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

            PrettyOutput.print(f"Analyzing repository at '{os.path.abspath(repo_path)}' from {start_date_str} to {end_date_str}", OutputType.INFO)

            original_branch = self._run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_path).stdout.strip()
            PrettyOutput.print(f"Original branch is '{original_branch}'. Will checkout back to it after analysis.", OutputType.INFO)
            
            # Try to determine the main branch name
            main_branch = "main"
            try:
                self._run_command(["git", "show-ref", "--verify", f"refs/heads/{main_branch}"], cwd=repo_path)
            except subprocess.CalledProcessError:
                main_branch = "master" # Fallback to master
                PrettyOutput.print("Branch 'main' not found, falling back to 'master'.", OutputType.WARNING)


            results_csv = "Month,LinesOfCode\n"
            current_date = start_date

            while current_date <= end_date:
                month_end = current_date + relativedelta(months=1) - relativedelta(days=1)
                month_display = current_date.strftime("%Y-%m")
                PrettyOutput.print(f"Processing month: {month_display}...", OutputType.INFO)

                try:
                    commit_hash_result = self._run_command(
                        ["git", "rev-list", "-n", "1", f"--before={month_end.strftime('%Y-%m-%d')} 23:59:59", main_branch],
                        cwd=repo_path
                    )
                    commit_hash = commit_hash_result.stdout.strip()
                except subprocess.CalledProcessError:
                    commit_hash = None

                lines_of_code = 0
                if commit_hash:
                    with tempfile.NamedTemporaryFile(mode='w+', delete=True) as temp_f:
                        self._run_command(["git", "checkout", commit_hash, "--quiet"], cwd=repo_path)
                        
                        # Run loc and save output
                        loc_command = ["loc", f"--include={file_types}", "."]
                        loc_result = self._run_command(loc_command, cwd=repo_path)
                        temp_f.write(loc_result.stdout)
                        temp_f.seek(0)
                        
                        # Parse the output robustly
                        for line in temp_f:
                            if line.strip().lower().startswith(tuple(ft.lower() for ft in file_types.split(','))):
                                 # Assumes format: Language Files Lines Blank Comment Code
                                 parts = line.split()
                                 if len(parts) >= 6:
                                     lines_of_code += int(parts[-1])


                results_csv += f"{month_display},{lines_of_code}\n"
                current_date += relativedelta(months=1)

            # Checkout back to the original branch
            self._run_command(["git", "checkout", original_branch, "--quiet"], cwd=repo_path)
            PrettyOutput.print(f"Successfully checked out back to branch '{original_branch}'.", OutputType.SUCCESS)

            return {"success": True, "stdout": results_csv.strip(), "stderr": ""}

        except Exception as e:
            PrettyOutput.print(f"An error occurred: {e}", OutputType.ERROR)
            # Attempt to checkout back to original branch on failure
            try:
                self._run_command(["git", "checkout", original_branch, "--quiet"], cwd=repo_path)
                PrettyOutput.print(f"Recovered and checked out back to branch '{original_branch}'.", OutputType.WARNING)
            except Exception as e2:
                PrettyOutput.print(f"Could not check out back to original branch: {e2}", OutputType.ERROR)
            return {"success": False, "stdout": "", "stderr": str(e)}
