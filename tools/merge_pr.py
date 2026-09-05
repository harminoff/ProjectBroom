"""Wait for Project Broom CI before merging, even without branch protection."""
import argparse
import json
import subprocess
import time

REPOSITORY = "harminoff/ProjectBroom"
REQUIRED = {("CI", "source-and-python"), ("CI", "native-bridge"),
            ("Engine integration", "build-engine")}
FIELDS = "state,isDraft,baseRefName,headRefOid,mergeable,statusCheckRollup,mergeCommit"


def gh(*args):
    result = subprocess.run(["gh", *args], capture_output=True, text=True, check=True)
    return result.stdout


def snapshot(pr):
    return json.loads(gh("pr", "view", str(pr), "--repo", REPOSITORY, "--json", FIELDS))


def ready(pr, expected_head):
    """Return readiness, or fail on unsafe/failed state. Missing checks wait."""
    if pr["headRefOid"] != expected_head:
        raise RuntimeError("PR head changed; review the new commit and rerun.")
    if pr["state"] != "OPEN" or pr["isDraft"] or pr["baseRefName"] != "main":
        raise RuntimeError("Expected an open, non-draft PR targeting main.")
    if pr["mergeable"] == "CONFLICTING":
        raise RuntimeError("PR has merge conflicts.")
    checks = pr.get("statusCheckRollup") or []
    found = set()
    pending = pr["mergeable"] != "MERGEABLE"
    for check in checks:
        if check.get("__typename") != "CheckRun":
            if check.get("state") in ("FAILURE", "ERROR"):
                raise RuntimeError("A commit status failed.")
            pending |= check.get("state") != "SUCCESS"
            continue
        key = (check.get("workflowName"), check.get("name"))
        if check.get("status") != "COMPLETED":
            pending = True
        elif check.get("conclusion") != "SUCCESS":
            # Required jobs always run; even the content-only engine gate
            # reports SUCCESS. Never accept missing, skipped or neutral gates.
            raise RuntimeError(f"Check did not succeed: {key}: {check.get('conclusion')}")
        else:
            found.add(key)
    return not pending and REQUIRED <= found


def publish(pr, expected_head, merge=False, timeout=3600, interval=15):
    deadline = time.monotonic() + timeout
    while True:
        if ready(snapshot(pr), expected_head):
            break
        if time.monotonic() >= deadline:
            raise TimeoutError("CI is pending or required checks are missing; nothing merged.")
        time.sleep(min(interval, max(0, deadline - time.monotonic())))
    if not merge:
        return "All required checks passed; check-only mode, nothing merged."
    # Re-read the current head and checks immediately before submitting.
    if not ready(snapshot(pr), expected_head):
        raise RuntimeError("Checks changed before merge; nothing merged.")
    gh("pr", "merge", str(pr), "--repo", REPOSITORY, "--squash",
       "--match-head-commit", expected_head)
    result = snapshot(pr)
    if result["state"] != "MERGED" or not result.get("mergeCommit"):
        raise RuntimeError("Merge was not confirmed; inspect GitHub before retrying.")
    return f"Merged PR #{pr}: {result['mergeCommit']['oid']}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pr", type=int)
    parser.add_argument("--head", required=True, help="Full reviewed PR head SHA")
    parser.add_argument("--merge", action="store_true", help="Squash-merge after checks pass")
    parser.add_argument("--timeout", type=int, default=3600, help="Wait limit in seconds; 0 checks once")
    args = parser.parse_args()
    if args.timeout < 0 or len(args.head) != 40 or any(c not in "0123456789abcdef" for c in args.head):
        parser.error("Supply a full lowercase SHA and a nonnegative timeout.")
    print(f"Checking PR #{args.pr} at {args.head}; waiting for all three CI gates.", flush=True)
    try:
        print(publish(args.pr, args.head, args.merge, args.timeout), flush=True)
    except (RuntimeError, TimeoutError, subprocess.CalledProcessError, ValueError, KeyError) as exc:
        parser.exit(1, f"Stopped: {exc}\n")


if __name__ == "__main__":
    main()
