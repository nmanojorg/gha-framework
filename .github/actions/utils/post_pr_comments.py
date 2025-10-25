import argparse
import json
import os
import sys
import requests

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post SpotBugs report as a PR comment on GitHub.")
    parser.add_argument("--repo", required=True, help="GitHub repository in the form owner/repo")
    parser.add_argument("--pr", required=True, type=int, help="Pull request number")
    parser.add_argument("--token", required=True, help="GitHub token with repo permissions")
    parser.add_argument("--report", required=True, help="Path to SpotBugs report file")
    parser.add_argument("--title", required=True, help="Title for the comment section")
    args = parser.parse_args()

    if not os.path.isfile(args.report):
        print(f"SpotBugs report not found at {args.report}", file=sys.stderr)
        sys.exit(0)

    with open(args.report, "r", encoding="utf-8") as f:
        report_content = f.read()

    comment_body = f"### {args.title}\n```text\n{report_content}\n```"
    url = f"https://api.github.com/repos/{args.repo}/issues/{args.pr}/comments"
    headers = {
        "Authorization": f"token {args.token}",
        "Content-Type": "application/json"
    }
    payload = json.dumps({"body": comment_body})

    response = requests.post(url, headers=headers, data=payload)
    print(f"GitHub API status code: {response.status_code}")
    print(response.text)
    response.raise_for_status()

