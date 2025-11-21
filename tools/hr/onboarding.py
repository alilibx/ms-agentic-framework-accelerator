"""Employee onboarding tools - Manage new hire onboarding process."""

from typing import Annotated
from datetime import datetime, timedelta
from tools._decorators import tool


@tool(
    domain="hr",
    description="Create onboarding checklist for new employee",
    tags=["hr", "onboarding", "new-hire", "checklist", "welcome"],
    mock=True,
)
def create_onboarding_checklist(
    employee_name: Annotated[str, "New employee name"],
    role: Annotated[str, "Job role/title"],
    start_date: Annotated[str, "Start date (YYYY-MM-DD)"],
    department: Annotated[str, "Department"] = "Engineering",
) -> str:
    """Create onboarding checklist for a new employee.

    Args:
        employee_name: Name of the new employee
        role: Job title/role
        start_date: Start date in YYYY-MM-DD format
        department: Department name

    Returns:
        Formatted onboarding checklist

    Example:
        >>> create_onboarding_checklist("Alex Chen", "Software Engineer", "2025-12-01")
        "Onboarding Checklist for Alex Chen..."
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        return "❌ **Error:** Invalid date format. Use YYYY-MM-DD"

    checklist_id = f"OB-{start.strftime('%Y%m%d')}-{hash(employee_name) % 1000:03d}"

    result = f"""
🎉 **Welcome Onboarding Checklist**

**New Employee:** {employee_name}
**Role:** {role}
**Department:** {department}
**Start Date:** {start.strftime('%A, %B %d, %Y')}
**Checklist ID:** {checklist_id}

---

**BEFORE DAY 1 (HR):**
   ☐ Send welcome email with first day details
   ☐ Create company email account
   ☐ Order laptop and equipment
   ☐ Set up building access badge
   ☐ Add to company directory
   ☐ Prepare workstation
   ☐ Schedule orientation sessions
   ☐ Assign onboarding buddy

**DAY 1 - Welcome & Setup:**
   ☐ Welcome meeting with HR
   ☐ Office tour and introductions
   ☐ IT setup (laptop, accounts, software)
   ☐ Review employee handbook
   ☐ Complete HR paperwork
   ☐ Benefits enrollment
   ☐ Security training
   ☐ Meet with manager

**WEEK 1 - Orientation:**
   ☐ Team introduction meetings
   ☐ Review role expectations and goals
   ☐ Access to necessary tools and systems
   ☐ Company culture overview
   ☐ Meet with onboarding buddy
   ☐ Department overview presentation
   ☐ Set up 1-on-1 meetings
   ☐ Review first project/assignment

**WEEK 2-4 - Integration:**
   ☐ Shadow team members
   ☐ Complete required training courses
   ☐ First project assignment
   ☐ Regular check-ins with manager
   ☐ Meet with cross-functional teams
   ☐ Review performance expectations
   ☐ Set 30-60-90 day goals

**30 DAYS:**
   ☐ 30-day check-in meeting
   ☐ Feedback session with manager
   ☐ Complete onboarding survey
   ☐ Review progress on goals

**60 DAYS:**
   ☐ 60-day review meeting
   ☐ Expand responsibilities
   ☐ Identify development opportunities

**90 DAYS:**
   ☐ 90-day performance review
   ☐ End of probation assessment
   ☐ Career development planning
   ☐ Confirm permanent employment

---

**Key Contacts:**
   • HR Partner: Alice Johnson (alice.j@company.com)
   • IT Support: it-support@company.com
   • Manager: [To be assigned]
   • Onboarding Buddy: [To be assigned]

**Important Resources:**
   • Employee Handbook: intranet/handbook
   • IT Setup Guide: intranet/it-setup
   • Benefits Portal: benefits.company.com
   • Learning Platform: learn.company.com

⏰ **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()

    return result


@tool(
    domain="hr",
    description="Get onboarding status and progress for new employee",
    tags=["hr", "onboarding", "status", "progress", "tracking"],
    mock=True,
)
def get_onboarding_status(
    employee_id: Annotated[str, "Employee ID or name"],
) -> str:
    """Check onboarding progress for a new employee.

    Args:
        employee_id: Employee ID or name

    Returns:
        Onboarding progress report

    Example:
        >>> get_onboarding_status("EMP006")
        "Onboarding Progress: 45% complete..."
    """
    result = """
📊 **Onboarding Progress Report**

**Employee:** Alex Chen (EMP006)
**Role:** Software Engineer
**Start Date:** December 1, 2025
**Days Elapsed:** 5 days
**Current Phase:** Week 1 - Orientation

---

**Overall Progress:** 45% Complete

**Completed Tasks (15/33):**
   ✅ Welcome email sent
   ✅ Email account created
   ✅ Laptop ordered and received
   ✅ Building access badge ready
   ✅ Added to company directory
   ✅ Workstation prepared
   ✅ Welcome meeting with HR
   ✅ Office tour completed
   ✅ IT setup completed
   ✅ Employee handbook reviewed
   ✅ HR paperwork completed
   ✅ Benefits enrollment started
   ✅ Security training completed
   ✅ Manager meeting held
   ✅ Team introductions done

**In Progress (3/33):**
   🔄 Benefits enrollment (waiting for selections)
   🔄 Training courses (2 of 5 completed)
   🔄 Setting up development environment

**Upcoming This Week (5/33):**
   ⏳ Review role expectations
   ⏳ Access to project management tools
   ⏳ Company culture overview
   ⏳ Meet with onboarding buddy
   ⏳ Department overview presentation

**Pending (10/33):**
   ☐ First project assignment
   ☐ Shadow team members
   ☐ Cross-functional team meetings
   ☐ And 7 more tasks...

---

**Milestone Progress:**
   ✅ Before Day 1: Complete (100%)
   🔄 Day 1: Complete (100%)
   🔄 Week 1: In Progress (60%)
   ☐ Week 2-4: Not Started (0%)
   ☐ 30 Days: Not Started (0%)
   ☐ 60 Days: Not Started (0%)
   ☐ 90 Days: Not Started (0%)

**Next Check-in:** Week 1 Review - December 8, 2025

**Action Items:**
   • HR: Follow up on benefits selections
   • Manager: Assign first project by Dec 7
   • IT: Complete dev environment setup
   • Buddy: Schedule coffee chat

**Manager Feedback:**
   "Alex is settling in well. Very engaged during meetings and asking great questions."

⏰ **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()

    return result


@tool(
    domain="hr",
    description="Schedule new hire orientation session",
    tags=["hr", "onboarding", "orientation", "schedule", "training"],
    mock=True,
)
def schedule_orientation(
    employee_name: Annotated[str, "Employee name"],
    session_type: Annotated[str, "Orientation type: company, department, it, benefits"],
    date: Annotated[str, "Preferred date (YYYY-MM-DD)"],
    time: Annotated[str, "Preferred time (HH:MM)"] = "10:00",
) -> str:
    """Schedule an orientation session for new employee.

    Args:
        employee_name: Name of the employee
        session_type: Type of orientation (company, department, it, benefits)
        date: Preferred date
        time: Preferred time

    Returns:
        Orientation session confirmation

    Example:
        >>> schedule_orientation("Alex Chen", "company", "2025-12-01", "10:00")
        "Company orientation scheduled for Alex Chen..."
    """
    try:
        session_date = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    except ValueError:
        return "❌ **Error:** Invalid date/time format"

    session_types = {
        "company": {
            "title": "Company Orientation",
            "duration": "2 hours",
            "host": "Alice Johnson (HR Manager)",
            "location": "Conference Room A",
            "topics": [
                "Company history and mission",
                "Culture and values",
                "Organizational structure",
                "Employee handbook review",
                "Q&A session"
            ]
        },
        "department": {
            "title": "Department Orientation",
            "duration": "90 minutes",
            "host": "Jane Smith (Engineering Manager)",
            "location": "Engineering Area",
            "topics": [
                "Team structure and roles",
                "Current projects overview",
                "Development processes",
                "Tools and workflows",
                "Team rituals and meetings"
            ]
        },
        "it": {
            "title": "IT Systems Setup",
            "duration": "1 hour",
            "host": "IT Support Team",
            "location": "IT Help Desk",
            "topics": [
                "Account setup and passwords",
                "Email and calendar",
                "VPN and security",
                "Software installations",
                "Support resources"
            ]
        },
        "benefits": {
            "title": "Benefits Orientation",
            "duration": "1 hour",
            "host": "Alice Johnson (HR Manager)",
            "location": "HR Office",
            "topics": [
                "Health insurance options",
                "401(k) and retirement",
                "PTO and leave policies",
                "Additional perks",
                "Enrollment process"
            ]
        }
    }

    session = session_types.get(session_type.lower(), session_types["company"])

    result = f"""
✅ **Orientation Session Scheduled**

📅 **{session['title']}**

**Attendee:** {employee_name}
**Date:** {session_date.strftime('%A, %B %d, %Y')}
**Time:** {session_date.strftime('%I:%M %p')} - {(session_date + timedelta(hours=2)).strftime('%I:%M %p')}
**Duration:** {session['duration']}
**Host:** {session['host']}
**Location:** {session['location']}

**Agenda:**
    """.strip()

    for i, topic in enumerate(session['topics'], 1):
        result += f"\n   {i}. {topic}"

    result += f"""

**What to Bring:**
   • Notepad and pen
   • Questions you may have
   • Laptop (if applicable)

**Pre-reading:**
   • Employee handbook (sent via email)
   • New hire welcome packet

**Calendar Invite:**
   ✅ Sent to {employee_name.split()[0].lower()}@company.com
   ✅ Reminder set for 30 minutes before

**Next Steps:**
   • Review pre-reading materials
   • Prepare any questions
   • Confirm attendance (reply to calendar invite)

💡 **Note:** If you need to reschedule, please contact HR at least 24 hours in advance.

⏰ **Scheduled:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()

    return result


@tool(
    domain="hr",
    description="Assign onboarding buddy to new employee",
    tags=["hr", "onboarding", "buddy", "mentor", "pairing"],
    mock=True,
)
def assign_onboarding_buddy(
    new_employee: Annotated[str, "New employee name"],
    buddy_name: Annotated[str, "Onboarding buddy name"] = "",
    auto_assign: Annotated[bool, "Auto-assign best match"] = True,
) -> str:
    """Assign an onboarding buddy to help new employee.

    Args:
        new_employee: Name of new employee
        buddy_name: Specific buddy to assign (or leave empty for auto-assign)
        auto_assign: Automatically find best match

    Returns:
        Buddy assignment confirmation

    Example:
        >>> assign_onboarding_buddy("Alex Chen", auto_assign=True)
        "Onboarding buddy assigned: Sarah Lee..."
    """
    if not buddy_name and auto_assign:
        buddy_name = "Sarah Lee"
        reason = "Same team, 2 years experience, previous buddy success"
    elif buddy_name:
        reason = "Manually assigned"
    else:
        return "❌ **Error:** Please provide buddy_name or set auto_assign=True"

    result = f"""
🤝 **Onboarding Buddy Assigned**

**New Employee:** {new_employee}
**Onboarding Buddy:** {buddy_name}
**Assignment Reason:** {reason}

**Buddy Profile:**
   • Name: {buddy_name}
   • Role: Software Engineer
   • Department: Engineering
   • Experience: 2 years at company
   • Previous buddy assignments: 3 successful onboardings
   • Contact: {buddy_name.lower().replace(' ', '.')}@company.com

**Buddy Responsibilities:**
   ✓ Be the go-to person for questions
   ✓ Help navigate company culture
   ✓ Introduce to team members
   ✓ Weekly check-in meetings (first month)
   ✓ Lunch/coffee chats
   ✓ Share tips and best practices
   ✓ Provide informal feedback

**First Meeting Scheduled:**
   • Date: First day, after IT setup
   • Duration: 30 minutes
   • Format: Informal coffee chat
   • Location: Cafeteria

**Meeting Cadence:**
   • Week 1: Daily check-ins (15 min)
   • Week 2-4: 3x per week (15 min)
   • Month 2-3: Weekly (30 min)
   • After 3 months: As needed

**Resources for Buddy:**
   • Buddy guide and checklist sent
   • FAQ document shared
   • Support from HR team
   • Recognition in quarterly meeting

**Success Metrics:**
   • Regular check-ins completed
   • New employee satisfaction score
   • Integration milestones met
   • 90-day retention

**Support:**
   • HR Contact: Alice Johnson
   • Questions: hr@company.com
   • Buddy Community: #onboarding-buddies

💡 **Both parties have been notified via email with next steps!**

⏰ **Assigned:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()

    return result
