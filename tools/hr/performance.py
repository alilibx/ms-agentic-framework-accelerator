"""Performance management tools - Reviews, goals, and feedback."""

from typing import Annotated
from datetime import datetime, timedelta
from tools._decorators import tool


@tool(
    domain="hr",
    description="Create or update employee performance goals",
    tags=["hr", "performance", "goals", "objectives", "okr"],
    mock=True,
)
def set_performance_goals(
    employee_id: Annotated[str, "Employee ID"] = "",
    goal_type: Annotated[str, "Goal type: quarterly, annual, project"] = "quarterly",
    goals: Annotated[str, "Comma-separated list of goals"] = "",
) -> str:
    """Set performance goals for an employee.

    Args:
        employee_id: Employee ID (defaults to current user)
        goal_type: Type of goals (quarterly, annual, project)
        goals: Comma-separated goals

    Returns:
        Goal setting confirmation

    Example:
        >>> set_performance_goals("EMP001", "quarterly", "Launch feature X, Improve code coverage to 80%")
        "Performance goals set successfully..."
    """
    if not goals:
        return "❌ **Error:** Please provide at least one goal"

    goal_list = [g.strip() for g in goals.split(",")]

    period_map = {
        "quarterly": "Q4 2025",
        "annual": "2025",
        "project": "Project-based"
    }
    period = period_map.get(goal_type.lower(), "Q4 2025")

    result = f"""
🎯 **Performance Goals Set**

**Employee:** John Doe (EMP001)
**Period:** {period}
**Goal Type:** {goal_type.title()}
**Status:** Active

**Goals ({len(goal_list)}):**
    """.strip()

    for i, goal in enumerate(goal_list, 1):
        result += f"\n\n{i}. **{goal}**"
        result += f"\n   • Status: Not Started"
        result += f"\n   • Target Date: {(datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')}"
        result += f"\n   • Weight: {100 // len(goal_list)}%"
        result += f"\n   • Metrics: To be defined"

    result += f"""

**Review Schedule:**
   • Mid-period Check-in: {(datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')}
   • Final Review: {(datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')}
   • Manager: Jane Smith

**Success Criteria:**
   • Goals should be SMART (Specific, Measurable, Achievable, Relevant, Time-bound)
   • Regular progress updates expected
   • Mid-period adjustment if needed

**Next Steps:**
   1. Review goals with manager
   2. Break down into actionable tasks
   3. Set up tracking metrics
   4. Schedule regular check-ins

💡 **Tip:** Update progress weekly to stay on track!

⏰ **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()

    return result


@tool(
    domain="hr",
    description="Submit performance review for employee",
    tags=["hr", "performance", "review", "evaluation", "feedback"],
    mock=True,
)
def submit_performance_review(
    employee_id: Annotated[str, "Employee ID to review"],
    review_period: Annotated[str, "Review period (e.g., Q4 2025, Annual 2025)"],
    rating: Annotated[str, "Overall rating: exceeds, meets, needs-improvement, unsatisfactory"],
    strengths: Annotated[str, "Key strengths and achievements"] = "",
    areas_for_improvement: Annotated[str, "Areas for development"] = "",
) -> str:
    """Submit a performance review (manager function).

    Args:
        employee_id: Employee being reviewed
        review_period: Review period
        rating: Overall performance rating
        strengths: Employee strengths
        areas_for_improvement: Development areas

    Returns:
        Review submission confirmation

    Example:
        >>> submit_performance_review("EMP001", "Q4 2025", "exceeds",
                "Strong technical skills", "Work on communication")
        "Performance review submitted..."
    """
    rating_emojis = {
        "exceeds": "⭐",
        "meets": "✅",
        "needs-improvement": "⚠️",
        "unsatisfactory": "❌"
    }
    emoji = rating_emojis.get(rating.lower(), "✅")

    review_id = f"REV-{datetime.now().strftime('%Y%m%d')}-{hash(employee_id) % 1000:03d}"

    result = f"""
{emoji} **Performance Review Submitted**

**Review ID:** {review_id}
**Employee:** John Doe (EMP001)
**Reviewer:** Jane Smith (Manager)
**Period:** {review_period}
**Overall Rating:** {rating.title()}

---

**PERFORMANCE SUMMARY:**

**Overall Assessment:** {emoji} {rating.title()}
    """.strip()

    if strengths:
        result += f"""

**Key Strengths & Achievements:**
   {strengths}

**Specific Examples:**
   • Successfully led the migration to microservices
   • Mentored 2 junior engineers
   • Improved system performance by 40%
   • Consistently delivered high-quality code
        """.strip()

    if areas_for_improvement:
        result += f"""

**Areas for Development:**
   {areas_for_improvement}

**Development Plan:**
   • Take communication skills workshop
   • Practice presenting in team meetings
   • Shadow senior team members
   • Set specific improvement goals
        """.strip()

    result += f"""

**Core Competencies Assessment:**
   Technical Skills: {emoji} Exceeds Expectations
   Communication: ✅ Meets Expectations
   Collaboration: {emoji} Exceeds Expectations
   Leadership: ✅ Meets Expectations
   Innovation: {emoji} Exceeds Expectations

**Goal Achievement:**
   • Goals Set: 4
   • Goals Achieved: 3
   • Goals In Progress: 1
   • Achievement Rate: 75%

**Attendance & Conduct:**
   • Attendance: Excellent
   • Punctuality: Excellent
   • Policy Compliance: Excellent

**Recommendations:**
   • Salary Increase: Recommended (+8%)
   • Promotion: Consider for L6 in next cycle
   • Bonus: Eligible for performance bonus
   • Development: Leadership training

**Next Review:** {(datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')}

**Status:** Pending Employee Acknowledgment

**Next Steps:**
   1. Review will be shared with employee
   2. Schedule 1-on-1 discussion meeting
   3. Employee can add comments
   4. HR will review and finalize
   5. Development plan created

⏰ **Submitted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()

    return result


@tool(
    domain="hr",
    description="Get performance review status and history",
    tags=["hr", "performance", "review", "history", "status"],
    mock=True,
)
def get_review_status(
    employee_id: Annotated[str, "Employee ID"] = "",
    include_history: Annotated[bool, "Include review history"] = False,
) -> str:
    """Check performance review status and history.

    Args:
        employee_id: Employee ID (defaults to current user)
        include_history: Include historical reviews

    Returns:
        Review status and history

    Example:
        >>> get_review_status("EMP001", include_history=True)
        "Current review status and historical performance..."
    """
    result = f"""
📊 **Performance Review Status**

**Employee:** John Doe (EMP001)
**Current Period:** Q4 2025

**Upcoming Review:**
   • Type: Quarterly Review
   • Due Date: {(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')}
   • Reviewer: Jane Smith (Manager)
   • Status: In Progress

**Current Goals Progress:**
   1. ✅ Launch Feature X - 100% Complete
   2. 🔄 Improve Code Coverage to 80% - 65% Complete
   3. 🔄 Mentor Junior Engineer - In Progress
   4. ⏳ Reduce Tech Debt - Not Started

**Recent Feedback:**
   • "Great work on the feature launch!" - Jane Smith (2 days ago)
   • "Code reviews are thorough and helpful" - Mike Chen (1 week ago)
    """.strip()

    if include_history:
        result += """

**Performance History:**

**Q3 2025:**
   • Rating: ⭐ Exceeds Expectations
   • Goals Achievement: 100% (4/4)
   • Key Highlight: Led successful project delivery
   • Salary Impact: +5% increase

**Q2 2025:**
   • Rating: ✅ Meets Expectations
   • Goals Achievement: 75% (3/4)
   • Key Highlight: Improved system reliability
   • Development Focus: Leadership skills

**Q1 2025:**
   • Rating: ✅ Meets Expectations
   • Goals Achievement: 100% (4/4)
   • Key Highlight: Strong technical contributions
   • Note: First review in role

**Annual 2024:**
   • Rating: ⭐ Exceeds Expectations
   • Goals Achievement: 90% (9/10)
   • Promotion: Promoted to Senior Engineer
   • Bonus: 15% performance bonus

**Trends:**
   • Performance: ↗️ Improving
   • Goal Achievement: 🎯 Consistently high
   • Growth: 📈 On track for next level
        """.strip()

    result += f"""

**Development Plan:**
   • Enroll in leadership training
   • Present at next engineering all-hands
   • Lead one major project per quarter
   • Continue mentoring program

**Career Path:**
   • Current: L5 Senior Software Engineer
   • Next Level: L6 Staff Engineer
   • Target Timeline: 6-12 months
   • Requirements: Leadership + technical excellence

⏰ **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()

    return result


@tool(
    domain="hr",
    description="Provide feedback to employee or peer",
    tags=["hr", "feedback", "recognition", "improvement", "peer"],
    mock=True,
)
def give_feedback(
    recipient: Annotated[str, "Employee receiving feedback"],
    feedback_text: Annotated[str, "Feedback content"],
    feedback_type: Annotated[str, "Type: praise, constructive, peer-review"] = "praise",
    anonymous: Annotated[bool, "Submit anonymously"] = False,
) -> str:
    """Give feedback to employee or peer.

    Args:
        recipient: Person receiving feedback
        feedback_type: Type of feedback
        feedback_text: Feedback content
        anonymous: Submit anonymously

    Returns:
        Feedback submission confirmation

    Example:
        >>> give_feedback("John Doe", "praise", "Excellent work on the API redesign!")
        "Feedback submitted successfully..."
    """
    feedback_emojis = {
        "praise": "🌟",
        "constructive": "💡",
        "peer-review": "👥"
    }
    emoji = feedback_emojis.get(feedback_type.lower(), "💬")

    from_text = "Anonymous" if anonymous else "Jane Smith"

    result = f"""
{emoji} **Feedback Submitted**

**To:** {recipient}
**From:** {from_text}
**Type:** {feedback_type.title()}
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Feedback:**
{feedback_text}

**Delivery:**
   • Recipient will be notified
   • Added to performance record
   • Manager will be CC'd (if significant)
   • Visible in next review

**Impact:**
   • Contributes to performance assessment
   • Builds culture of continuous feedback
   • Supports employee development

💡 **Thank you for contributing to a feedback culture!**
    """.strip()

    return result


@tool(
    domain="hr",
    description="Schedule performance review meeting",
    tags=["hr", "performance", "review", "meeting", "1on1"],
    mock=True,
)
def schedule_review_meeting(
    employee_id: Annotated[str, "Employee ID"],
    review_type: Annotated[str, "Type: quarterly, annual, mid-year, check-in"],
    date: Annotated[str, "Preferred date (YYYY-MM-DD)"],
    duration_minutes: Annotated[int, "Meeting duration in minutes"] = 60,
) -> str:
    """Schedule a performance review meeting.

    Args:
        employee_id: Employee being reviewed
        review_type: Type of review
        date: Meeting date
        duration_minutes: Duration in minutes

    Returns:
        Meeting confirmation

    Example:
        >>> schedule_review_meeting("EMP001", "quarterly", "2025-12-15", 60)
        "Review meeting scheduled..."
    """
    try:
        meeting_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "❌ **Error:** Invalid date format. Use YYYY-MM-DD"

    result = f"""
📅 **Performance Review Meeting Scheduled**

**Meeting Type:** {review_type.title()} Review
**Employee:** John Doe (EMP001)
**Reviewer:** Jane Smith (Manager)
**Date:** {meeting_date.strftime('%A, %B %d, %Y')}
**Time:** 2:00 PM - {(datetime.strptime('14:00', '%H:%M') + timedelta(minutes=duration_minutes)).strftime('%I:%M %p')}
**Duration:** {duration_minutes} minutes
**Location:** Conference Room B (or Zoom link sent)

**Agenda:**
   1. Review period overview (5 min)
   2. Goal achievement discussion (15 min)
   3. Performance feedback (20 min)
   4. Strengths and development areas (10 min)
   5. Next period goals (15 min)
   6. Questions and next steps (10 min)

**Preparation Required:**

   **Employee:**
   • Review your goals and achievements
   • Prepare self-assessment
   • List accomplishments and challenges
   • Think about career goals
   • Prepare questions

   **Manager:**
   • Complete performance evaluation
   • Gather peer feedback
   • Review goal progress
   • Prepare development recommendations
   • Compensation discussion (if applicable)

**Materials Shared:**
   • Performance review document
   • Goal tracking spreadsheet
   • Peer feedback summary
   • Development resources

**Calendar Invite:**
   ✅ Sent to both parties
   ✅ Reminder 1 day before
   ✅ Reminder 1 hour before

**Confidentiality:**
   • Discussion is confidential
   • Notes will be documented
   • Copy provided to employee
   • Stored in HR system

⏰ **Scheduled:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()

    return result
