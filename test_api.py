#!/usr/bin/env python
"""
Test script for Smart City Dashboard API
Demonstrates the two main functionalities:
1. n8n Webhook Receiver (POST /api/webhook/save-stats/)
2. Dashboard Data Endpoint (GET /api/dashboard/)
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000/api"


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_webhook_save_stats():
    """Test the n8n webhook receiver endpoint."""
    print_section("TEST 1: n8n Webhook Receiver - Save Stats")

    url = f"{BASE_URL}/webhook/save-stats/"

    # Test payload matching the specification
    payload = {
        "energyOptimizationData": {
            "summary": {
                "total_consumption": 150.5,
                "anomalies": True,
                "average_power": 450.2,
            },
            "statistics": {"voltage": {"min": 210, "max": 230, "average": 220}},
        },
        "wasteTrackingData": {
            "avgFill": 75.5,
            "criticalCount": 3,
            "warningCount": 5,
            "warningLocations": ["Point A", "Point B", "Point C"],
        },
    }

    print("📤 Sending webhook data to:", url)
    print("\n📋 Payload:")
    print(json.dumps(payload, indent=2))

    try:
        response = requests.post(url, json=payload)
        print(f"\n✅ Status Code: {response.status_code}")
        print("\n📥 Response:")
        print(json.dumps(response.json(), indent=2))

        if response.status_code == 201:
            print("\n✅ SUCCESS: Both EnergyLog and WasteLog records created!")
            return True
        else:
            print("\n❌ FAILED: Unexpected status code")
            return False

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False


def test_webhook_partial_data():
    """Test webhook with only energy data."""
    print_section("TEST 2: Webhook with Partial Data (Energy Only)")

    url = f"{BASE_URL}/webhook/save-stats/"

    payload = {
        "energyOptimizationData": {
            "summary": {
                "total_consumption": 200.8,
                "anomalies": False,
                "average_power": 380.5,
            },
            "statistics": {"voltage": {"min": 215, "max": 225, "average": 220}},
        }
    }

    print("📤 Sending only energy data...")
    print(json.dumps(payload, indent=2))

    try:
        response = requests.post(url, json=payload)
        print(f"\n✅ Status Code: {response.status_code}")
        print(json.dumps(response.json(), indent=2))

        if response.status_code == 201:
            print("\n✅ SUCCESS: EnergyLog created (WasteLog skipped)")
            return True
        else:
            return False

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False


def create_test_report():
    """Create a test citizen report."""
    print_section("TEST 3: Create Citizen Report")

    url = f"{BASE_URL}/reports/create/"

    payload = {
        "reporter_name": "Nguyen Van Test",
        "issue_type": "traffic",
        "description": "Traffic light malfunction at main intersection. Causing delays.",
        "location": "123 Main Street, Da Nang",
    }

    print("📤 Creating citizen report...")
    print(json.dumps(payload, indent=2))

    try:
        response = requests.post(url, json=payload)
        print(f"\n✅ Status Code: {response.status_code}")
        print(json.dumps(response.json(), indent=2))

        if response.status_code == 201:
            print("\n✅ SUCCESS: Citizen report created!")
            return True
        else:
            return False

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False


def test_dashboard():
    """Test the dashboard data endpoint."""
    print_section("TEST 4: Dashboard Data Endpoint")

    url = f"{BASE_URL}/dashboard/"

    print("📤 Fetching dashboard data from:", url)

    try:
        response = requests.get(url)
        print(f"\n✅ Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("\n📊 Dashboard Data:")
            print(json.dumps(data, indent=2))

            # Analyze response
            print("\n" + "-" * 80)
            print("📈 Dashboard Summary:")
            print("-" * 80)

            # Traffic
            if data.get("traffic"):
                traffic = data["traffic"]
                print(f"\n🚦 Traffic Status:")
                print(f"   Address: {traffic.get('address', 'N/A')}")
                print(
                    f"   Status: {traffic.get('status_code', 'N/A')} ({traffic.get('status_color', 'N/A')})"
                )
                print(f"   Congestion: {traffic.get('congestion_rate', 0) * 100:.1f}%")
                print(f"   Speed: {traffic.get('flow_speed', 0)} km/h")
                print(f"   Incidents: {traffic.get('incident_count', 0)}")
            else:
                print("\n🚦 Traffic: No data available")

            # Energy
            if data.get("energy"):
                energy = data["energy"]
                print(f"\n⚡ Energy Status:")
                print(f"   Consumption: {energy.get('total_consumption', 0)} kWh")
                print(f"   Avg Power: {energy.get('avg_power', 0)} W")
                print(
                    f"   Anomalies: {'⚠️ YES' if energy.get('anomalies_detected') else '✅ NO'}"
                )
                voltage = energy.get("voltage_stats", {})
                print(
                    f"   Voltage: {voltage.get('min', 0)}-{voltage.get('max', 0)}V (avg: {voltage.get('average', 0)}V)"
                )
            else:
                print("\n⚡ Energy: No data available")

            # Waste
            if data.get("waste"):
                waste = data["waste"]
                print(f"\n🗑️  Waste Status:")
                print(f"   Avg Fill: {waste.get('avg_fill_level', 0):.1f}%")
                print(f"   Critical Bins: {waste.get('critical_count', 0)}")
                print(f"   Warning Bins: {waste.get('warning_count', 0)}")
                locations = waste.get("warning_locations", [])
                if locations:
                    print(f"   Warning Locations: {', '.join(locations)}")
            else:
                print("\n🗑️  Waste: No data available")

            # Reports
            reports = data.get("reports", {})
            print(f"\n📝 Citizen Reports:")
            print(f"   Total: {reports.get('total_count', 0)}")
            print(f"   Pending: {reports.get('pending_count', 0)}")
            print(f"   Recent: {len(reports.get('recent', []))} reports")

            print("\n✅ SUCCESS: Dashboard data fetched successfully!")
            return True
        else:
            print("\n❌ FAILED: Unexpected status code")
            return False

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("  🏙️  SMART CITY DASHBOARD API TEST SUITE")
    print("=" * 80)
    print("\n⏳ Starting tests...\n")

    results = []

    # Test 1: Webhook with full data
    results.append(("Webhook - Full Data", test_webhook_save_stats()))
    sleep(1)

    # Test 2: Webhook with partial data
    results.append(("Webhook - Partial Data", test_webhook_partial_data()))
    sleep(1)

    # Test 3: Create citizen report
    results.append(("Create Report", create_test_report()))
    sleep(1)

    # Test 4: Dashboard
    results.append(("Dashboard Data", test_dashboard()))

    # Summary
    print_section("TEST RESULTS SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")

    print(f"\n📊 Final Score: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
