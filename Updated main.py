import argparse
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Example JIRA data fetcher (replace with real JIRA API integration)
def fetch_jira_issues(project_id, fix_version=None):
    return [
        {
            "key": f"{project_id}-101",
            "summary": "Login bug",
            "description": "",
            "epic": "EPIC-01",
            "created": "2024-02-10T12:00:00.000+0000",
            "acceptance_criteria": "TBD"
        },
        {
            "key": f"{project_id}-102",
            "summary": "",
            "description": "Broken link on page",
            "epic": "",
            "created": "2025-04-10T12:00:00.000+0000",
            "acceptance_criteria": "Given user is on homepage When they click Then they navigate"
        },
        {
            "key": f"{project_id}-103",
            "summary": "Validation test",
            "description": "Check field values",
            "epic": "EPIC-02",
            "created": "2025-04-10T12:00:00.000+0000",
            "acceptance_criteria": "Given user is on homepage When they click Then they navigate"
        }
    ]

MANDATORY_FIELDS = ["summary", "description", "epic"]

def check_missing_fields(issue):
    missing = {}
    for field in MANDATORY_FIELDS:
        if not issue.get(field, "").strip():
            missing[field] = "MISSING"
    return missing

def validate_acceptance_criteria(ac_text):
    ac_text = ac_text.lower()
    if all(k in ac_text for k in ["given", "when", "then"]):
        return "Valid"
    return "Not in Given-When-Then format"

def create_html_report(issues, project_id, fix_version):
    old_issues = []
    new_issues = []
    ac_text_map = {}
    duplicate_acs = set()

    for issue in issues:
        created_date = datetime.strptime(issue["created"][:10], "%Y-%m-%d")
        age = (datetime.now() - created_date).days
        if age > 60:
            old_issues.append(issue)
        else:
            new_issues.append(issue)
        ac = issue.get("acceptance_criteria", "").strip().lower()
        if ac:
            if ac in ac_text_map:
                duplicate_acs.add(ac)
            else:
                ac_text_map[ac] = issue["key"]

    def build_table(title, issues_list):
        html = f"<h3>{title}</h3>"
        html += "<table border='1' cellpadding='5' cellspacing='0'>"
        html += "<tr><th>JIRA</th><th>Summary</th><th>Missing Fields</th><th>Acceptance Criteria</th></tr>"
        for issue in issues_list:
            missing_fields = check_missing_fields(issue)
            missing_str = ', '.join(missing_fields.keys()) if missing_fields else "None"
            ac_text = issue.get("acceptance_criteria", "")
            ac_status = validate_acceptance_criteria(ac_text)
            ac_warning = " (Duplicate)" if ac_text.strip().lower() in duplicate_acs else ""
            html += f"<tr><td>{issue['key']}</td><td>{issue['summary'] or '---'}</td>"
            html += f"<td style='color:red'>{missing_str}</td>"
            html += f"<td style='color:red'>{ac_status}{ac_warning}</td></tr>"
        html += "</table>"
        return html

    html_report = f"<h2>Validation Report for {project_id} - Fix Version: {fix_version or 'N/A'}</h2>"
    html_report += build_table("🔴 More than 60 Days Old", old_issues)
    html_report += build_table("🟢 60 Days Old or Less", new_issues)
    return html_report

def send_email(html_body, to_address, project_id, fix_version, total_issues):
    from_address = "noreply@yourbank.com"
    subject = f"[JIRA Validation] {project_id} - {fix_version or 'No Version'} - {total_issues} Issues Scanned"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = to_address
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP("your.smtp.server", 25) as server:
            server.sendmail(from_address, [to_address], msg.as_string())
        print(f"Email sent to {to_address}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def run_report(project_id, fix_version, to_address):
    issues = fetch_jira_issues(project_id, fix_version)
    html = create_html_report(issues, project_id, fix_version)
    send_email(html, to_address, project_id, fix_version, len(issues))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JIRA Validator with Enhanced Acceptance Criteria Validation")
    parser.add_argument("--project-id", required=True, help="JIRA project ID (e.g., SPK)")
    parser.add_argument("--fix-version", required=False, help="Optional fix version")
    parser.add_argument("--mail-group", required=True, help="Email group to send results")

    args = parser.parse_args()
    run_report(args.project_id, args.fix_version, args.mail_group)
