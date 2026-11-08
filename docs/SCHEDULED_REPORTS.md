# Scheduled reports

StratifyIQ can email the weekly or monthly report to every Admin automatically, using
Windows Task Scheduler. Nothing runs in the background inside the app, so the computer
must be on at the scheduled time.

## 1. Test it once by hand

In the project folder, with the environment active and the email settings set:

    python -m app.send_reports --period weekly

Each Admin is listed with `sent` or `not sent`.

## 2. Schedule it weekly

1. Open **Task Scheduler** (Start menu) and choose **Create Basic Task**.
2. Name: `StratifyIQ weekly report`. Trigger: **Weekly**, Monday, 08:00.
3. Action: **Start a program**. Program: `send-weekly-report.bat`, with its full path.
4. Finish, then right-click the task and choose **Run** to test it.

For a monthly report, create a second task with a **Monthly** trigger and change the
`--period` argument in a copy of the batch file to `monthly`.

## Security

`send-weekly-report.bat` contains the database password and the email App Password.
Keep the file private, do not share it, and revoke the App Password if the file is copied.
