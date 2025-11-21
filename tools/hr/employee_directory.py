"""Employee directory tools - Search and view employee information."""

from typing import Annotated
from datetime import datetime
from tools._decorators import tool


@tool(
    domain="hr",
    description="Search for employees by name, department, or role",
    tags=["hr", "employee", "search", "directory", "lookup"],
    mock=True,
)
def search_employees(
    query: Annotated[str, "Search query (name, department, or role)"],
    search_by: Annotated[str, "Search field: 'name', 'department', 'role', 'all'"] = "all",
    limit: Annotated[int, "Maximum number of results to return"] = 10,
) -> str:
    """Search for employees in the company directory.

    Args:
        query: Search query string
        search_by: Field to search ('name', 'department', 'role', 'all')
        limit: Maximum results to return

    Returns:
        Formatted string with matching employees

    Example:
        >>> search_employees("engineering", search_by="department")
        "Found 5 employees in Engineering:
        1. John Doe - Senior Engineer
        2. Jane Smith - Engineering Manager..."
    """
    # Mock employee data
    mock_employees = [
        {
            "id": "EMP001",
            "name": "John Doe",
            "email": "john.doe@company.com",
            "department": "Engineering",
            "role": "Senior Software Engineer",
            "manager": "Jane Smith",
            "location": "San Francisco, CA",
            "start_date": "2020-03-15"
        },
        {
            "id": "EMP002",
            "name": "Jane Smith",
            "email": "jane.smith@company.com",
            "department": "Engineering",
            "role": "Engineering Manager",
            "manager": "Bob Johnson",
            "location": "San Francisco, CA",
            "start_date": "2018-01-10"
        },
        {
            "id": "EMP003",
            "name": "Alice Johnson",
            "email": "alice.j@company.com",
            "department": "Human Resources",
            "role": "HR Manager",
            "manager": "Bob Johnson",
            "location": "New York, NY",
            "start_date": "2019-06-01"
        },
        {
            "id": "EMP004",
            "name": "Bob Johnson",
            "email": "bob.johnson@company.com",
            "department": "Executive",
            "role": "Chief Technology Officer",
            "manager": "CEO",
            "location": "San Francisco, CA",
            "start_date": "2017-11-20"
        },
        {
            "id": "EMP005",
            "name": "Carol White",
            "email": "carol.white@company.com",
            "department": "Marketing",
            "role": "Marketing Specialist",
            "manager": "David Brown",
            "location": "Austin, TX",
            "start_date": "2021-08-15"
        },
    ]

    # Filter based on search criteria
    query_lower = query.lower()
    results = []

    for emp in mock_employees:
        if search_by == "all":
            if (query_lower in emp["name"].lower() or
                query_lower in emp["department"].lower() or
                query_lower in emp["role"].lower()):
                results.append(emp)
        elif search_by == "name" and query_lower in emp["name"].lower():
            results.append(emp)
        elif search_by == "department" and query_lower in emp["department"].lower():
            results.append(emp)
        elif search_by == "role" and query_lower in emp["role"].lower():
            results.append(emp)

    # Limit results
    results = results[:limit]

    if not results:
        return f"❌ No employees found matching '{query}' in {search_by}"

    # Format output
    result = f"🔍 **Employee Search Results** ({len(results)} found)\n\n"
    result += f"**Query:** '{query}' in {search_by}\n\n"

    for i, emp in enumerate(results, 1):
        result += f"""
{i}. 👤 **{emp['name']}** ({emp['id']})
   📧 {emp['email']}
   💼 {emp['role']}
   🏢 {emp['department']}
   👔 Reports to: {emp['manager']}
   📍 {emp['location']}
   📅 Start Date: {emp['start_date']}
        """.strip() + "\n\n"

    return result.strip()


@tool(
    domain="hr",
    description="Get detailed information about a specific employee",
    tags=["hr", "employee", "details", "profile", "info"],
    mock=True,
)
def get_employee_details(
    employee_id: Annotated[str, "Employee ID (e.g., EMP001)"] = "",
    email: Annotated[str, "Employee email address"] = "",
) -> str:
    """Get detailed information about an employee.

    Args:
        employee_id: Employee ID to lookup
        email: Employee email (alternative to employee_id)

    Returns:
        Formatted employee profile

    Example:
        >>> get_employee_details(employee_id="EMP001")
        "Employee Profile: John Doe
        Role: Senior Software Engineer..."
    """
    if not employee_id and not email:
        return "❌ **Error:** Please provide either employee_id or email"

    # Mock employee database
    mock_employee = {
        "id": "EMP001",
        "name": "John Doe",
        "email": "john.doe@company.com",
        "phone": "+1 (555) 123-4567",
        "department": "Engineering",
        "role": "Senior Software Engineer",
        "level": "L5",
        "manager": "Jane Smith (EMP002)",
        "location": "San Francisco, CA",
        "office": "HQ - Floor 3, Desk 42",
        "start_date": "2020-03-15",
        "employment_type": "Full-time",
        "team": "Backend Platform",
        "skills": ["Python", "Go", "Kubernetes", "AWS"],
        "projects": ["Payment System v2", "API Gateway"],
        "next_review": "2025-12-15",
        "vacation_days": 15,
        "sick_days": 5
    }

    result = f"""
👤 **Employee Profile**

**Basic Information:**
   • Name: {mock_employee['name']}
   • Employee ID: {mock_employee['id']}
   • Email: {mock_employee['email']}
   • Phone: {mock_employee['phone']}

**Position:**
   • Role: {mock_employee['role']}
   • Level: {mock_employee['level']}
   • Department: {mock_employee['department']}
   • Team: {mock_employee['team']}
   • Manager: {mock_employee['manager']}

**Employment Details:**
   • Type: {mock_employee['employment_type']}
   • Start Date: {mock_employee['start_date']}
   • Next Review: {mock_employee['next_review']}

**Location:**
   • Office: {mock_employee['location']}
   • Workspace: {mock_employee['office']}

**Skills:**
   {', '.join(mock_employee['skills'])}

**Current Projects:**
   • {chr(10).join(f"  • {p}" for p in mock_employee['projects'])}

**Time Off Balance:**
   • Vacation Days: {mock_employee['vacation_days']} remaining
   • Sick Days: {mock_employee['sick_days']} remaining

⏰ **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()

    return result


@tool(
    domain="hr",
    description="Get organization chart or team hierarchy",
    tags=["hr", "org-chart", "hierarchy", "team", "structure"],
    mock=True,
)
def get_org_chart(
    department: Annotated[str, "Department name (leave empty for full org chart)"] = "",
) -> str:
    """Get organization chart or department hierarchy.

    Args:
        department: Specific department to view (or empty for full org)

    Returns:
        Formatted organization chart

    Example:
        >>> get_org_chart(department="Engineering")
        "Engineering Department Org Chart:
        CTO - Bob Johnson
        ├── Engineering Manager - Jane Smith..."
    """
    if department:
        dept_lower = department.lower()
        if "engineering" in dept_lower:
            result = """
🏢 **Engineering Department - Organization Chart**

**Bob Johnson** - Chief Technology Officer
├── **Jane Smith** - Engineering Manager
│   ├── John Doe - Senior Software Engineer
│   ├── Mike Chen - Software Engineer
│   └── Sarah Lee - Junior Software Engineer
└── **Alex Kumar** - Engineering Manager
    ├── Tom Wilson - Senior DevOps Engineer
    └── Lisa Park - DevOps Engineer
            """.strip()
        elif "hr" in dept_lower or "human" in dept_lower:
            result = """
🏢 **Human Resources Department - Organization Chart**

**Alice Johnson** - HR Manager
├── Mary Thompson - HR Specialist
├── David Kim - Recruiter
└── Emily Davis - HR Coordinator
            """.strip()
        else:
            result = f"📋 Department '{department}' org chart coming soon..."
    else:
        result = """
🏢 **Company Organization Chart**

**CEO** - Sarah Williams
├── **CTO** - Bob Johnson (Technology)
│   ├── Engineering Manager - Jane Smith
│   └── Engineering Manager - Alex Kumar
├── **CFO** - Michael Brown (Finance)
│   ├── Senior Accountant - James Wilson
│   └── Financial Analyst - Emma Davis
├── **HR Manager** - Alice Johnson (Human Resources)
│   ├── HR Specialist - Mary Thompson
│   └── Recruiter - David Kim
└── **CMO** - Rachel Green (Marketing)
    ├── Marketing Manager - Carol White
    └── Social Media Manager - Kevin Lee
        """.strip()

    result += f"\n\n⏰ **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    return result
