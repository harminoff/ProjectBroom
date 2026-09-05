import unittest
from unittest.mock import patch
from tools import merge_pr

SHA = "a" * 40


def green():
    return dict(state="OPEN", isDraft=False, baseRefName="main", headRefOid=SHA,
                mergeable="MERGEABLE", statusCheckRollup=[
                    dict(__typename="CheckRun", workflowName=w, name=n,
                         status="COMPLETED", conclusion="SUCCESS")
                    for w, n in sorted(merge_pr.REQUIRED)])


class MergeGateTests(unittest.TestCase):
    def test_all_three_required(self):
        self.assertTrue(merge_pr.ready(green(), SHA))
        for size in range(3):
            pr = green()
            pr["statusCheckRollup"] = pr["statusCheckRollup"][:size]
            self.assertFalse(merge_pr.ready(pr, SHA))

    def test_pending_waits(self):
        for status in ("QUEUED", "IN_PROGRESS", "WAITING"):
            pr = green()
            pr["statusCheckRollup"][0]["status"] = status
            self.assertFalse(merge_pr.ready(pr, SHA))

    def test_unsuccessful_checks_rejected(self):
        for conclusion in ("FAILURE", "CANCELLED", "TIMED_OUT", "SKIPPED", "NEUTRAL", None):
            pr = green()
            pr["statusCheckRollup"][0]["conclusion"] = conclusion
            with self.assertRaises(RuntimeError):
                merge_pr.ready(pr, SHA)

    def test_wrong_workflow_does_not_substitute(self):
        pr = green()
        pr["statusCheckRollup"][0]["workflowName"] = "Unrelated"
        self.assertFalse(merge_pr.ready(pr, SHA))

    def test_unsafe_pr_rejected(self):
        for key, value in (("state", "CLOSED"), ("isDraft", True),
                           ("baseRefName", "other"), ("headRefOid", "b" * 40),
                           ("mergeable", "CONFLICTING")):
            pr = green()
            pr[key] = value
            with self.assertRaises(RuntimeError):
                merge_pr.ready(pr, SHA)

    def test_timeout_never_merges(self):
        pr = green()
        pr["statusCheckRollup"] = []
        with patch.object(merge_pr, "snapshot", return_value=pr), patch.object(merge_pr, "gh") as gh:
            with self.assertRaises(TimeoutError):
                merge_pr.publish(12, SHA, merge=True, timeout=0)
            gh.assert_not_called()

    def test_head_change_before_merge_stops(self):
        changed = green()
        changed["headRefOid"] = "b" * 40
        with patch.object(merge_pr, "snapshot", side_effect=[green(), changed]), patch.object(merge_pr, "gh") as gh:
            with self.assertRaises(RuntimeError):
                merge_pr.publish(12, SHA, merge=True)
            gh.assert_not_called()

    def test_check_rerun_before_merge_stops(self):
        changed = green()
        changed["statusCheckRollup"][0]["status"] = "IN_PROGRESS"
        with patch.object(merge_pr, "snapshot", side_effect=[green(), changed]), patch.object(merge_pr, "gh") as gh:
            with self.assertRaises(RuntimeError):
                merge_pr.publish(12, SHA, merge=True)
            gh.assert_not_called()

    def test_merge_is_atomic_for_reviewed_head(self):
        merged = dict(state="MERGED", mergeCommit={"oid": "c" * 40})
        with patch.object(merge_pr, "snapshot", side_effect=[green(), green(), merged]), patch.object(merge_pr, "gh") as gh:
            self.assertIn("Merged PR #12", merge_pr.publish(12, SHA, merge=True))
            gh.assert_called_once_with("pr", "merge", "12", "--repo", merge_pr.REPOSITORY,
                                       "--squash", "--match-head-commit", SHA)

    def test_default_is_read_only(self):
        with patch.object(merge_pr, "snapshot", return_value=green()), patch.object(merge_pr, "gh") as gh:
            self.assertIn("check-only", merge_pr.publish(12, SHA))
            gh.assert_not_called()

    def test_api_failure_never_merges(self):
        with patch.object(merge_pr, "snapshot", side_effect=RuntimeError("API failed")), patch.object(merge_pr, "gh") as gh:
            with self.assertRaises(RuntimeError):
                merge_pr.publish(12, SHA, merge=True)
            gh.assert_not_called()


if __name__ == "__main__":
    unittest.main()
