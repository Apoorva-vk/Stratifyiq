# Connecting StratifyIQ to Jira Cloud

## 1. Create an API token

1. Sign in at id.atlassian.com.
2. Go to **Security → Create and manage API tokens**.
3. Click **Create API token**, name it `stratifyiq`, and copy it. You can't view it again.

## 2. Set the settings in the backend window

Use your own site address, email and token. Keep the token private.

    $env:JIRA_BASE_URL="https://YOUR-SITE.atlassian.net"
    $env:JIRA_EMAIL="your.jira.email@example.com"
    $env:JIRA_API_TOKEN="paste-the-token-here"

Then restart the backend (Ctrl+C, then `python -m uvicorn app.main:app --reload`).

## 3. Use it

1. Open a project → **Manage**. The **Jira** card shows "Connected to …".
2. Click **Test connection**. It shows your Jira name.
3. Edit the JQL if needed, for example `project = DEMO ORDER BY created DESC`, then click **Import issues**.
4. Later, click **Sync status** to update done/not done from Jira.

## What is and isn't synced

- Imported: issue summary (as the task name), original time estimate (as hours, default 1 hour), and done/not done status.
- Not yet synced: assignees (tasks stay unassigned, so you can assign them in StratifyIQ), comments and attachments.
- Read-only: StratifyIQ never changes anything in Jira.

## Troubleshooting

- "Jira rejected the email or API token": check `JIRA_EMAIL` is your Atlassian login email and the token is current.
- "Jira could not run this query": check the JQL works in Jira's search first.
- "Could not reach Jira": check the site address and your internet connection.
