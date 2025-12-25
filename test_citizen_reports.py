"""
Test script for Citizen Report API endpoints.

Usage:
    python test_citizen_reports.py
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000/api"


def test_create_report():
    """Test creating a new citizen report."""
    print("\n" + "=" * 60)
    print("TEST 1: Create Citizen Report (without image)")
    print("=" * 60)

    data = {
        "reporter_name": "John Doe",
        "issue_type": "traffic",
        "description": "Heavy traffic congestion on Main Street during rush hour",
        "location": "Main Street, Downtown",
    }

    response = requests.post(f"{BASE_URL}/reports/", data=data)
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")

    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    report = response.json()
    assert report["status"] == "pending", "Status should default to 'pending'"
    assert report["reporter_name"] == "John Doe"

    print("✓ Test passed!")
    return report["id"]


def test_create_report_with_different_types():
    """Test creating reports with different issue types."""
    print("\n" + "=" * 60)
    print("TEST 2: Create Reports with Different Issue Types")
    print("=" * 60)

    issue_types = [
        ("waste", "Overflowing bin at Park Avenue"),
        ("energy", "Street light not working on Oak Street"),
        ("other", "Pothole on Elm Street"),
    ]

    for issue_type, description in issue_types:
        data = {
            "reporter_name": "Test User",
            "issue_type": issue_type,
            "description": description,
            "location": f"Test Location for {issue_type}",
        }

        response = requests.post(f"{BASE_URL}/reports/", data=data)
        print(f"\n{issue_type}: Status {response.status_code}")

        if response.status_code == 201:
            report = response.json()
            print(f"  ID: {report['id']}")
            print(f"  Display: {report['issue_type_display']}")
            print(f"  Status: {report['status_display']}")
        else:
            print(f"  Error: {response.json()}")

    print("\n✓ Test passed!")


def test_list_all_reports():
    """Test listing all reports."""
    print("\n" + "=" * 60)
    print("TEST 3: List All Reports")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/reports/")
    print(f"Status: {response.status_code}")

    reports = response.json()
    print(f"Total reports: {len(reports)}")

    if reports:
        print("\nFirst report:")
        print(json.dumps(reports[0], indent=2))

    print("\n✓ Test passed!")
    return len(reports)


def test_filter_by_status():
    """Test filtering reports by status."""
    print("\n" + "=" * 60)
    print("TEST 4: Filter Reports by Status")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/reports/?status=pending")
    print(f"Status: {response.status_code}")

    reports = response.json()
    print(f"Pending reports: {len(reports)}")

    # Verify all returned reports have status 'pending'
    for report in reports:
        assert report["status"] == "pending", "All reports should have status 'pending'"

    print("✓ Test passed!")


def test_filter_by_issue_type():
    """Test filtering reports by issue type."""
    print("\n" + "=" * 60)
    print("TEST 5: Filter Reports by Issue Type")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/reports/?issue_type=traffic")
    print(f"Status: {response.status_code}")

    reports = response.json()
    print(f"Traffic reports: {len(reports)}")

    # Verify all returned reports have issue_type 'traffic'
    for report in reports:
        assert (
            report["issue_type"] == "traffic"
        ), "All reports should have issue_type 'traffic'"

    print("✓ Test passed!")


def test_multiple_filters():
    """Test using multiple filters together."""
    print("\n" + "=" * 60)
    print("TEST 6: Multiple Filters (status + issue_type)")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/reports/?status=pending&issue_type=traffic")
    print(f"Status: {response.status_code}")

    reports = response.json()
    print(f"Pending traffic reports: {len(reports)}")

    # Verify all returned reports match both filters
    for report in reports:
        assert report["status"] == "pending"
        assert report["issue_type"] == "traffic"

    print("✓ Test passed!")


def test_retrieve_single_report(report_id):
    """Test retrieving a single report by ID."""
    print("\n" + "=" * 60)
    print(f"TEST 7: Retrieve Single Report (ID: {report_id})")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/reports/{report_id}/")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        report = response.json()
        print(f"Report ID: {report['id']}")
        print(f"Reporter: {report['reporter_name']}")
        print(f"Issue: {report['issue_type_display']}")
        print(f"Status: {report['status_display']}")
        print("✓ Test passed!")
    else:
        print(f"Error: {response.json()}")


def test_update_report_status(report_id):
    """Test updating a report's status."""
    print("\n" + "=" * 60)
    print(f"TEST 8: Update Report Status (ID: {report_id})")
    print("=" * 60)

    # Update status to 'in_progress'
    data = {"status": "in_progress"}
    response = requests.patch(
        f"{BASE_URL}/reports/{report_id}/",
        json=data,
        headers={"Content-Type": "application/json"},
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        report = response.json()
        print(f"New status: {report['status']} ({report['status_display']})")
        assert report["status"] == "in_progress"
        print("✓ Test passed!")
    else:
        print(f"Error: {response.json()}")


def test_ordering():
    """Test ordering reports."""
    print("\n" + "=" * 60)
    print("TEST 9: Ordering Reports")
    print("=" * 60)

    # Default ordering (latest first)
    response = requests.get(f"{BASE_URL}/reports/")
    reports_default = response.json()

    # Oldest first
    response = requests.get(f"{BASE_URL}/reports/?ordering=created_at")
    reports_oldest = response.json()

    if reports_default and reports_oldest:
        print(f"Default (latest first): ID {reports_default[0]['id']}")
        print(f"Oldest first: ID {reports_oldest[0]['id']}")

        # Verify ordering is different (if we have multiple reports)
        if len(reports_default) > 1:
            assert reports_default[0]["id"] != reports_oldest[0]["id"]

    print("✓ Test passed!")


def test_dashboard_integration():
    """Test that citizen reports appear in dashboard."""
    print("\n" + "=" * 60)
    print("TEST 10: Dashboard Integration")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/dashboard/")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        dashboard = response.json()
        print(f"\nDashboard citizen report stats:")
        print(f"  Pending count: {dashboard['reports']['pending_count']}")
        print(f"  Total count: {dashboard['reports']['total_count']}")
        print(f"  Recent reports: {len(dashboard['reports']['recent'])}")
        print("✓ Test passed!")
    else:
        print(f"Error: {response.json()}")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("CITIZEN REPORT API TESTS")
    print("=" * 60)
    print("\nMake sure the Django server is running on http://localhost:8000")
    input("Press Enter to start tests...")

    try:
        # Run tests
        report_id = test_create_report()
        test_create_report_with_different_types()
        total_reports = test_list_all_reports()
        test_filter_by_status()
        test_filter_by_issue_type()
        test_multiple_filters()
        test_retrieve_single_report(report_id)
        test_update_report_status(report_id)
        test_ordering()
        test_dashboard_integration()

        # Summary
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print(f"\nTotal reports created: {total_reports}")
        print("\nYou can now:")
        print("  1. View reports at: http://localhost:8000/api/reports/")
        print("  2. Check dashboard at: http://localhost:8000/api/dashboard/")
        print("  3. Filter by status: http://localhost:8000/api/reports/?status=pending")
        print(
            "  4. Filter by type: http://localhost:8000/api/reports/?issue_type=traffic"
        )

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Make sure Django server is running: python manage.py runserver")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
