"""Jira Cloud connection (REST API v3). Read-only: it pulls issues in and never changes Jira.

Authentication is email plus an API token, sent with HTTP Basic auth. The token comes from
the environment only (JIRA_API_TOKEN). Create one at id.atlassian.com under Security → API tokens.
"""
import httpx

from app.config import settings

FIELDS = ["summary", "status", "timeoriginalestimate"]


class JiraError(Exception):
    pass


def configured() -> bool:
    return bool(settings.JIRA_BASE_URL and settings.JIRA_EMAIL and settings.JIRA_API_TOKEN)


def _client() -> httpx.Client:
    if not configured():
        raise JiraError("Jira is not connected. Set JIRA_BASE_URL, JIRA_EMAIL and JIRA_API_TOKEN in the backend window.")
    return httpx.Client(
        base_url=settings.JIRA_BASE_URL.rstrip("/"),
        auth=(settings.JIRA_EMAIL, settings.JIRA_API_TOKEN),
        headers={"Accept": "application/json"},
        timeout=20,
    )


def _check(response: httpx.Response) -> None:
    if response.status_code == 401:
        raise JiraError("Jira rejected the email or API token. Check JIRA_EMAIL and JIRA_API_TOKEN.")
    if response.status_code == 403:
        raise JiraError("Jira refused access. The account may not have permission to this project.")
    if response.status_code == 400:
        raise JiraError(f"Jira could not run this query: {response.text[:200]}")
    response.raise_for_status()


def test_connection() -> str:
    with _client() as client:
        r = client.get("/rest/api/3/myself")
        _check(r)
        return r.json().get("displayName", "connected")


def search(jql: str, max_results: int = 50) -> list[dict]:
    with _client() as client:
        r = client.post("/rest/api/3/search/jql", json={"jql": jql, "fields": FIELDS, "maxResults": max_results})
        _check(r)
        return r.json().get("issues", [])


def to_task(issue: dict) -> dict:
    """Maps a Jira issue to a StratifyIQ task. Hours come from the original estimate, default 1 hour."""
    fields = issue.get("fields", {})
    seconds = fields.get("timeoriginalestimate") or 0
    hours = round(seconds / 3600, 1) if seconds else 1.0
    done = (fields.get("status") or {}).get("statusCategory", {}).get("key") == "done"
    return {
        "key": issue["key"],
        "title": f"{issue['key']}: {fields.get('summary', '')}"[:200],
        "hours": max(hours, 0.5),
        "done": done,
    }
