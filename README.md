### Tests Report
This repository hosts the code used 
to generate a scheduled report on repositories' 
GitHub Actions' tests. 

`main.py` contains the core logic that triggers 
and evaluates the GitHub Actions tests throughout 
the repositories belonging to the GitHub accounts 
as pointed out in the `Credentials` class in `classes.py`. 

`.github/workflows/reporting.yml` contains the 
cron schedule and commands performed by the machine
to run `main.py`. We can also run this report by 
manually triggering it through the UI under the Actions 
tab for this repository.
