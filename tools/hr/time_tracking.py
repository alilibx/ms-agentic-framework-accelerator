"""Time tracking tools - Track work hours, overtime, and attendance."""

from typing import Annotated
from datetime import datetime, timedelta
from tools._decorators import tool


@tool(
    domain="hr",
    description="Log work hours for timesheet",
    tags=["hr", "time", "timesheet", "hours", "tracking"],
    mock=True,
)
def log_hours(
    date: Annotated[str, "Date (YYYY-MM-DD)"] = "",
    hours: Annotated[float, "Hours worked"] = 8.0,
    project: Annotated[str, "Project or task name"] = "General",
    description: Annotated[str, "Work description"] = "",
) -> str:
    """Log work hours for a specific date.

    Args:
        date: Date to log hours (defaults to today)
        hours: Number of hours worked
        project: Project or task name
        description: Description of work done

    Returns:
        Hours logged confirmation

    Example:
        >>> log_hours("2025-11-16", 8.5, "API Project", "Implemented authentication")
        "8.5 hours logged successfully..."
    """
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    try:
        log_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "❌ **Error:** Invalid date format. Use YYYY-MM-DD"

    if hours < 0 or hours > 24:
        return "❌ **Error:** Hours must be between 0 and 24"

    entry_id = f"TS-{log_date.strftime('%Y%m%d')}-{hash(project) % 1000:03d}"

    # Determine if overtime
    is_overtime = hours > 8
    regular_hours = min(hours, 8)
    overtime_hours = max(hours - 8, 0)

    result = f"""
✅ **Work Hours Logged**

**Entry ID:** {entry_id}
**Employee:** John Doe (EMP001)
**Date:** {log_date.strftime('%A, %B %d, %Y')}

**Hours Breakdown:**
   ⏰ Regular Hours: {regular_hours:.1f}
   {"⚡ Overtime Hours: " + f"{overtime_hours:.1f}" if is_overtime else ""}
   📊 Total Hours: {hours:.1f}

**Project/Task:** {project}
    """.strip()

    if description:
        result += f"\n**Description:** {description}"

    result += f"""

**Weekly Summary (Current Week):**
   • Monday: 8.0 hours
   • Tuesday: 8.0 hours
   • Wednesday: {hours:.1f} hours (today)
   • Total This Week: {16 + hours:.1f} hours
   • Remaining: {40 - (16 + hours):.1f} hours (for 40hr week)

**Timesheet Status:**
   • Period: Nov 11-17, 2025
   • Status: In Progress
   • Submit By: Nov 17, 2025 5:00 PM
   • Approver: Jane Smith

**Next Steps:**
   • Continue logging daily hours
   • Submit timesheet by Friday
   • Manager will review and approve

💡 **Reminder:** Log hours daily for accurate tracking!

⏰ **Logged:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()

    return result


@tool(
    domain="hr",
    description="Get timesheet summary for a period",
    tags=["hr", "timesheet", "summary", "hours", "report"],
    mock=True,
)
def get_timesheet_summary(
    period: Annotated[str, "Period: 'week', 'month', 'pay-period'"] = "week",
    start_date: Annotated[str, "Start date (YYYY-MM-DD) - optional"] = "",
) -> str:
    """Get timesheet summary for a period.

    Args:
        period: Time period to summarize
        start_date: Optional start date

    Returns:
        Timesheet summary

    Example:
        >>> get_timesheet_summary("week")
        "Weekly timesheet summary: 40 hours..."
    """
    if start_date:
        try:
            period_start = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            return "❌ **Error:** Invalid date format. Use YYYY-MM-DD"
    else:
        # Default to current week start (Monday)
        today = datetime.now()
        period_start = today - timedelta(days=today.weekday())

    if period == "week":
        period_end = period_start + timedelta(days=6)
        period_label = "Week"
    elif period == "month":
        period_end = period_start + timedelta(days=30)
        period_label = "Month"
    elif period == "pay-period":
        period_end = period_start + timedelta(days=13)
        period_label = "Pay Period"
    else:
        period_end = period_start + timedelta(days=6)
        period_label = "Week"

    result = f"""
📊 **Timesheet Summary - {period_label}**

**Employee:** John Doe (EMP001)
**Period:** {period_start.strftime('%b %d')} - {period_end.strftime('%b %d, %Y')}
**Status:** {"Submitted" if datetime.now() > period_end else "In Progress"}

**Hours Breakdown:**

   **Week 1:**
   • Monday (Nov 11): 8.0 hours - General Development
   • Tuesday (Nov 12): 8.5 hours - API Project (0.5 OT)
   • Wednesday (Nov 13): 8.0 hours - Bug Fixes
   • Thursday (Nov 14): 9.0 hours - Feature Development (1.0 OT)
   • Friday (Nov 15): 7.5 hours - Code Review
   • Subtotal: 41.0 hours

**Summary:**
   ⏰ Regular Hours: 38.5 hours
   ⚡ Overtime Hours: 2.5 hours
   📊 Total Hours: 41.0 hours
   🎯 Target Hours: 40.0 hours
   📈 Variance: +1.0 hours

**Project Allocation:**
   • API Project: 16.0 hours (39%)
   • General Development: 12.0 hours (29%)
   • Bug Fixes: 8.0 hours (20%)
   • Code Review: 5.0 hours (12%)

**Billable vs Non-Billable:**
   • Billable: 32.0 hours (78%)
   • Non-Billable: 9.0 hours (22%)

**Approval Status:**
   • Submitted: {(period_end + timedelta(days=2)).strftime('%Y-%m-%d')}
   • Approved By: Jane Smith
   • Approved On: {(period_end + timedelta(days=3)).strftime('%Y-%m-%d')}
   • Status: ✅ Approved

**Payment Information:**
   • Regular Pay: $3,080.00 (38.5 hrs × $80/hr)
   • Overtime Pay: $300.00 (2.5 hrs × $120/hr)
   • Total Gross: $3,380.00
   • Pay Date: {(period_end + timedelta(days=10)).strftime('%Y-%m-%d')}

💡 **Performance:** On track with expected hours

⏰ **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()

    return result


@tool(
    domain="hr",
    description="Submit timesheet for approval",
    tags=["hr", "timesheet", "submit", "approval"],
    mock=True,
)
def submit_timesheet(
    period_start: Annotated[str, "Period start date (YYYY-MM-DD)"],
    period_end: Annotated[str, "Period end date (YYYY-MM-DD)"],
) -> str:
    """Submit timesheet for manager approval.

    Args:
        period_start: Start of the period
        period_end: End of the period

    Returns:
        Submission confirmation

    Example:
        >>> submit_timesheet("2025-11-11", "2025-11-17")
        "Timesheet submitted for approval..."
    """
    try:
        start = datetime.strptime(period_start, "%Y-%m-%d")
        end = datetime.strptime(period_end, "%Y-%m-%d")
    except ValueError:
        return "❌ **Error:** Invalid date format. Use YYYY-MM-DD"

    if end < start:
        return "❌ **Error:** End date must be after start date"

    submission_id = f"TS-SUB-{start.strftime('%Y%m%d')}"

    result = f"""
✅ **Timesheet Submitted for Approval**

**Submission ID:** {submission_id}
**Employee:** John Doe (EMP001)
**Period:** {start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}
**Submitted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Summary:**
   • Total Hours: 41.0
   • Regular Hours: 38.5
   • Overtime Hours: 2.5
   • Days Worked: 5
   • Projects: 4

**Approver:** Jane Smith (Manager)
**Expected Response:** Within 2 business days

**Status Tracking:**
   1. ✅ Submitted by employee
   2. ⏳ Awaiting manager review
   3. ⏳ HR verification
   4. ⏳ Payroll processing

**What Happens Next:**
   • Manager receives notification
   • Review typically within 24-48 hours
   • You'll receive email when approved/rejected
   • If approved, forwarded to payroll

**Important Notes:**
   • Cannot edit after submission
   • Contact manager if changes needed
   • Approval required before next pay period
   • Late submission may delay payment

**View Status:**
   • Check email for updates
   • View in HR portal: hr.company.com/timesheets
   • Submission ID: {submission_id}

💡 **Tip:** Ensure all hours are accurate before submitting!

⏰ **Submitted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()

    return result


@tool(
    domain="hr",
    description="Check attendance record and statistics",
    tags=["hr", "attendance", "record", "punctuality", "stats"],
    mock=True,
)
def get_attendance_record(
    employee_id: Annotated[str, "Employee ID"] = "",
    period: Annotated[str, "Period: 'month', 'quarter', 'year'"] = "month",
) -> str:
    """Check employee attendance record.

    Args:
        employee_id: Employee ID (defaults to current user)
        period: Time period to check

    Returns:
        Attendance record and statistics

    Example:
        >>> get_attendance_record("EMP001", "month")
        "Attendance record for November 2025..."
    """
    period_map = {
        "month": "November 2025",
        "quarter": "Q4 2025",
        "year": "2025"
    }
    period_label = period_map.get(period.lower(), "November 2025")

    result = f"""
📅 **Attendance Record**

**Employee:** John Doe (EMP001)
**Period:** {period_label}
**Department:** Engineering

**Attendance Statistics:**
   ✅ Days Worked: 16 days
   🏖️ Vacation Days: 0 days
   🏥 Sick Days: 1 day
   👤 Personal Days: 0 days
   ❌ Absences (Unexcused): 0 days
   🕐 Late Arrivals: 2 times
   🏠 Remote Work: 5 days

**Work Schedule:**
   • Expected Days: 20 working days
   • Actual Days: 17 days
   • Attendance Rate: 85%
   • Punctuality Rate: 90%

**Recent Attendance:**
   • Nov 15: ✅ Present (9:00 AM - 6:00 PM)
   • Nov 14: ✅ Present (9:15 AM - 6:15 PM) - Late
   • Nov 13: ✅ Present (9:00 AM - 5:30 PM)
   • Nov 12: 🏠 Remote Work
   • Nov 11: ✅ Present (9:00 AM - 6:00 PM)
   • Nov 8: 🏥 Sick Leave
   • Nov 7: ✅ Present (9:05 AM - 5:45 PM) - Late

**Time Patterns:**
   • Average Arrival: 9:02 AM
   • Average Departure: 5:52 PM
   • Average Hours/Day: 8.2 hours
   • Most Productive Day: Tuesday
   • Preferred Remote Days: Friday

**Compliance:**
   ✅ Meeting minimum attendance requirements
   ✅ Remote work within policy (max 2 days/week)
   ✅ No attendance warnings
   ✅ Good standing

**Year-to-Date Summary:**
   • Total Days Worked: 210 days
   • Vacation Used: 10 days
   • Sick Leave Used: 4 days
   • Overall Attendance: 95%
   • Late Arrivals: 8 times
   • Perfect Attendance Months: 6

**Upcoming Leave:**
   • Dec 20-31: Approved Vacation (12 days)

💡 **Status:** Excellent attendance record!

⏰ **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()

    return result


@tool(
    domain="hr",
    description="Request overtime or log extra hours worked",
    tags=["hr", "overtime", "extra-hours", "compensation"],
    mock=True,
)
def request_overtime(
    date: Annotated[str, "Date overtime was worked (YYYY-MM-DD)"],
    hours: Annotated[float, "Overtime hours"],
    reason: Annotated[str, "Reason for overtime"],
    pre_approved: Annotated[bool, "Was this pre-approved?"] = False,
) -> str:
    """Request overtime pay or log extra hours.

    Args:
        date: Date overtime was worked
        hours: Number of overtime hours
        reason: Reason for the overtime
        pre_approved: Whether overtime was pre-approved

    Returns:
        Overtime request confirmation

    Example:
        >>> request_overtime("2025-11-16", 3.5, "Critical production issue", False)
        "Overtime request submitted..."
    """
    try:
        ot_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "❌ **Error:** Invalid date format. Use YYYY-MM-DD"

    if hours <= 0 or hours > 12:
        return "❌ **Error:** Overtime hours must be between 0 and 12"

    request_id = f"OT-{ot_date.strftime('%Y%m%d')}-{hash(reason) % 1000:03d}"

    # Calculate pay
    hourly_rate = 80
    overtime_rate = hourly_rate * 1.5
    overtime_pay = hours * overtime_rate

    result = f"""
{"✅" if pre_approved else "⏳"} **Overtime Request {"Logged" if pre_approved else "Submitted"}**

**Request ID:** {request_id}
**Employee:** John Doe (EMP001)
**Date:** {ot_date.strftime('%A, %B %d, %Y')}

**Overtime Details:**
   ⏰ Hours: {hours:.1f} hours
   💰 Rate: ${overtime_rate:.2f}/hour (1.5x regular)
   💵 Total Pay: ${overtime_pay:.2f}
   🔖 Pre-approved: {"Yes" if pre_approved else "No"}

**Reason:**
   {reason}

**Status:** {"Approved - Will be included in next payroll" if pre_approved else "Pending Manager Approval"}

**Approval Process:**
    """.strip()

    if pre_approved:
        result += """
   ✅ Pre-approved by manager
   ✅ Hours logged in timesheet
   ✅ Forwarded to payroll
   • Pay Date: Next pay period
        """.strip()
    else:
        result += """
   1. ⏳ Manager review (Jane Smith)
   2. ⏳ HR verification
   3. ⏳ Payroll processing
   • Expected Response: 1-2 business days
        """.strip()

    result += f"""

**Company Overtime Policy:**
   • Overtime must be approved in advance (when possible)
   • Rate: 1.5x regular hourly rate
   • Maximum: 12 hours per day
   • Weekend work: 2x rate (if applicable)
   • Holiday work: 2.5x rate

**This Pay Period:**
   • Total Overtime: {hours + 2.5:.1f} hours
   • Total OT Pay: ${(hours + 2.5) * overtime_rate:.2f}
   • Regular Hours: 38.5 hours

**Next Steps:**
   {"• Hours will appear in next timesheet" if pre_approved else "• Wait for manager approval"}
   • Track status with request ID
   • Contact HR with questions

💡 {"Thank you for your extra effort!" if pre_approved else "Reminder: Get pre-approval for planned overtime"}

⏰ **Submitted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()

    return result
