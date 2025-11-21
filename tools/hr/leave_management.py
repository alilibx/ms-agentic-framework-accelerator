"""Leave management tools - Handle vacation, sick leave, and time-off requests."""

from typing import Annotated
from datetime import datetime, timedelta
from tools._decorators import tool


@tool(
    domain="hr",
    description="Request time off or vacation leave",
    tags=["hr", "leave", "vacation", "time-off", "pto", "request"],
    mock=True,
)
def request_leave(
    start_date: Annotated[str, "Leave start date (YYYY-MM-DD)"],
    end_date: Annotated[str, "Leave end date (YYYY-MM-DD)"],
    leave_type: Annotated[str, "Leave type: vacation, sick, personal, unpaid"] = "vacation",
    reason: Annotated[str, "Reason for leave (optional)"] = "",
) -> str:
    """Request time off or leave.

    Args:
        start_date: Leave start date in YYYY-MM-DD format
        end_date: Leave end date in YYYY-MM-DD format
        leave_type: Type of leave (vacation, sick, personal, unpaid)
        reason: Optional reason for the leave

    Returns:
        Formatted leave request confirmation

    Example:
        >>> request_leave("2025-12-20", "2025-12-31", "vacation", "Holiday break")
        "Leave request submitted successfully..."
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        if end < start:
            return "❌ **Error:** End date cannot be before start date"

        days = (end - start).days + 1

    except ValueError:
        return "❌ **Error:** Invalid date format. Use YYYY-MM-DD"

    # Calculate request ID
    request_id = f"LR-{datetime.now().strftime('%Y%m%d')}-{hash(start_date) % 1000:03d}"

    # Leave type emojis
    leave_emojis = {
        "vacation": "🏖️",
        "sick": "🏥",
        "personal": "👤",
        "unpaid": "📅"
    }
    emoji = leave_emojis.get(leave_type.lower(), "📅")

    result = f"""
✅ **Leave Request Submitted Successfully!**

{emoji} **Request ID:** {request_id}

**Leave Details:**
   • Type: {leave_type.title()}
   • Start Date: {start.strftime('%A, %B %d, %Y')}
   • End Date: {end.strftime('%A, %B %d, %Y')}
   • Duration: {days} {'day' if days == 1 else 'days'}
   • Status: Pending Manager Approval

**Requested By:** John Doe (EMP001)
**Manager:** Jane Smith

**Request Timeline:**
   • Submitted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
   • Expected Response: Within 2 business days
    """.strip()

    if reason:
        result += f"\n\n**Reason:**\n   {reason}"

    result += """

**Next Steps:**
   1. Your manager will review this request
   2. You'll receive an email notification with the decision
   3. Check leave balance and calendar for conflicts

💡 **Tip:** You can check your request status using the leave request ID
    """.strip()

    return result


@tool(
    domain="hr",
    description="Check leave balance and available time off",
    tags=["hr", "leave", "balance", "pto", "vacation", "days"],
    mock=True,
)
def check_leave_balance(
    employee_id: Annotated[str, "Employee ID (leave empty for current user)"] = "",
) -> str:
    """Check leave balance and time off availability.

    Args:
        employee_id: Employee ID to check (defaults to current user)

    Returns:
        Formatted leave balance information

    Example:
        >>> check_leave_balance()
        "Leave Balance Summary:
        Vacation: 15 days remaining..."
    """
    # Mock leave balance data
    current_year = datetime.now().year

    result = f"""
📊 **Leave Balance Summary - {current_year}**

**Employee:** John Doe (EMP001)

**Available Leave:**
   🏖️  **Vacation Days:** 15 days remaining (out of 25 annual)
   🏥 **Sick Days:** 8 days remaining (out of 10 annual)
   👤 **Personal Days:** 3 days remaining (out of 5 annual)

**Used This Year:**
   • Vacation: 10 days
   • Sick Leave: 2 days
   • Personal: 2 days
   • Total Used: 14 days

**Upcoming Leave:**
   • Dec 20-31, 2025: Vacation (12 days) - Pending

**Accrual Rate:**
   • Vacation: 2.08 days/month
   • Sick Leave: 0.83 days/month
   • Personal: 0.42 days/month

**Policy Information:**
   • Vacation days carry over: Up to 5 days
   • Sick days carry over: No limit
   • Personal days: Use or lose
   • Notice required: 2 weeks for >5 consecutive days

⏰ **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()

    return result


@tool(
    domain="hr",
    description="View leave request status and history",
    tags=["hr", "leave", "status", "history", "requests"],
    mock=True,
)
def get_leave_status(
    request_id: Annotated[str, "Leave request ID (e.g., LR-20251116-042)"] = "",
    show_history: Annotated[bool, "Show all leave requests history"] = False,
) -> str:
    """Check leave request status or view history.

    Args:
        request_id: Specific request ID to check
        show_history: If True, show all historical requests

    Returns:
        Leave request status or history

    Example:
        >>> get_leave_status(request_id="LR-20251116-042")
        "Leave Request Status: Approved..."
    """
    if request_id:
        # Mock specific request
        result = f"""
📋 **Leave Request Status**

**Request ID:** {request_id}

**Status:** ✅ Approved

**Leave Details:**
   • Type: Vacation
   • Start: December 20, 2025
   • End: December 31, 2025
   • Duration: 12 days

**Approval Information:**
   • Approved By: Jane Smith (Manager)
   • Approved On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
   • Comments: "Enjoy your holiday break!"

**Timeline:**
   1. Requested: Nov 15, 2025 10:30 AM
   2. Manager Notified: Nov 15, 2025 10:31 AM
   3. Approved: Nov 15, 2025 02:45 PM

**Next Steps:**
   • Your calendar has been updated
   • Out-of-office auto-reply will activate on Dec 20
   • Ensure handoff is complete before leaving
        """.strip()

    elif show_history:
        result = """
📚 **Leave Request History**

**2025 Requests:**

1. ✅ **LR-20251116-042** - Approved
   • Vacation: Dec 20-31, 2025 (12 days)
   • Approved by: Jane Smith

2. ✅ **LR-20250901-123** - Approved
   • Vacation: Sep 1-5, 2025 (5 days)
   • Approved by: Jane Smith

3. ✅ **LR-20250615-089** - Approved
   • Sick Leave: Jun 15-16, 2025 (2 days)
   • Approved by: Jane Smith

4. ❌ **LR-20250401-067** - Denied
   • Personal: Apr 1-3, 2025 (3 days)
   • Denied by: Jane Smith
   • Reason: "Critical project deadline"

5. ✅ **LR-20250215-034** - Approved
   • Vacation: Feb 15-19, 2025 (5 days)
   • Approved by: Jane Smith

**Summary:**
   • Total Requests: 5
   • Approved: 4
   • Denied: 1
   • Pending: 0
        """.strip()
    else:
        result = """
📋 **Recent Leave Requests**

**Pending:**
   • None

**Recently Approved:**
   1. LR-20251116-042 - Vacation (Dec 20-31)

**Upcoming Leave:**
   • Dec 20-31, 2025: Holiday Break (12 days)

💡 Use `request_id` to see specific request details or `show_history=true` for full history
        """.strip()

    return result


@tool(
    domain="hr",
    description="Approve or deny leave requests (for managers)",
    tags=["hr", "leave", "approve", "deny", "manager", "review"],
    mock=True,
)
def review_leave_request(
    request_id: Annotated[str, "Leave request ID to review"],
    action: Annotated[str, "Action: 'approve' or 'deny'"],
    comments: Annotated[str, "Comments or reason for decision"] = "",
) -> str:
    """Approve or deny a leave request (manager function).

    Args:
        request_id: Leave request ID to review
        action: 'approve' or 'deny'
        comments: Optional comments for the employee

    Returns:
        Confirmation of review action

    Example:
        >>> review_leave_request("LR-20251116-042", "approve", "Enjoy your vacation!")
        "Leave request LR-20251116-042 approved successfully"
    """
    if action.lower() not in ["approve", "deny"]:
        return "❌ **Error:** Action must be 'approve' or 'deny'"

    action_emoji = "✅" if action.lower() == "approve" else "❌"
    action_text = "Approved" if action.lower() == "approve" else "Denied"

    result = f"""
{action_emoji} **Leave Request {action_text}**

**Request ID:** {request_id}
**Action:** {action_text}
**Reviewed By:** Jane Smith (Manager)
**Reviewed On:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Request Details:**
   • Employee: John Doe (EMP001)
   • Type: Vacation
   • Dates: Dec 20-31, 2025 (12 days)
    """.strip()

    if comments:
        result += f"\n\n**Manager Comments:**\n   \"{comments}\""

    result += f"""

**Next Steps:**
   • Employee has been notified via email
   • {"Calendar has been updated" if action.lower() == "approve" else "Employee can submit a new request"}
   • {"HR has been notified of the approval" if action.lower() == "approve" else "Request has been archived"}
    """.strip()

    return result


@tool(
    domain="hr",
    description="View team leave calendar and availability",
    tags=["hr", "leave", "calendar", "team", "availability", "coverage"],
    mock=True,
)
def get_team_calendar(
    department: Annotated[str, "Department or team name"] = "Engineering",
    month: Annotated[str, "Month to view (YYYY-MM)"] = "",
) -> str:
    """View team leave calendar and check availability.

    Args:
        department: Department or team to view
        month: Month in YYYY-MM format (defaults to current month)

    Returns:
        Team leave calendar

    Example:
        >>> get_team_calendar("Engineering", "2025-12")
        "Engineering Team - December 2025 Leave Calendar..."
    """
    if not month:
        month = datetime.now().strftime("%Y-%m")

    try:
        month_date = datetime.strptime(month, "%Y-%m")
        month_name = month_date.strftime("%B %Y")
    except ValueError:
        return "❌ **Error:** Invalid month format. Use YYYY-MM"

    result = f"""
📅 **{department} Team Leave Calendar - {month_name}**

**Team Availability:**

**Week 1 (Dec 1-7):**
   ✅ Full team available

**Week 2 (Dec 8-14):**
   ✅ Full team available

**Week 3 (Dec 15-21):**
   ⚠️  Reduced capacity
   • Mike Chen: Vacation (Dec 15-19)

**Week 4 (Dec 22-31):**
   🔴 Limited coverage
   • John Doe: Vacation (Dec 20-31)
   • Sarah Lee: Vacation (Dec 24-27)
   • Jane Smith: Working (On-call)

**Team Coverage:**
   • Available: 2 out of 5 team members
   • On Leave: 3 team members
   • Coverage Status: Adequate with on-call rotation

**Upcoming Leave (Next 3 Months):**
   • Jan 2026: No scheduled leave
   • Feb 2026: 1 person (Mike Chen, Feb 10-14)
   • Mar 2026: No scheduled leave

💡 **Recommendations:**
   • Consider staggering vacation schedules
   • Ensure knowledge transfer before Dec 20
   • Set up on-call rotation for critical systems

⏰ **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()

    return result
