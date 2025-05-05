
# JIRA Missing Fields Checker

## Setup

1. Install Python 3.x
2. Run `pip install -r requirements.txt`
3. Configure `.env` with JIRA and email credentials.

## Usage

```bash
python main.py --project SPK --fix-version "1.0" --mail-group "group@example.com"
```

## Output
- Sends HTML email report.
- Attaches Excel file with invalid JIRA issues.
