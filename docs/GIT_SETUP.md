# Putting the project on GitHub

1. Create an empty repository on github.com (for example `stratifyiq`). Do not add a README there.
2. In PowerShell, inside the project's `stratifyiq` folder:

       git init
       git add .
       git commit -m "StratifyIQ: MCA major project"
       git branch -M main
       git remote add origin https://github.com/YOUR-USERNAME/stratifyiq.git
       git push -u origin main

The included `.gitignore` keeps out the virtual environments, `node_modules`, the local
database file and `send-weekly-report.bat` (which contains passwords). Never commit those.
