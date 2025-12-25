"""
Test script for Newsletter Subscription API.

Usage:
    python test_newsletter.py
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"


def test_valid_subscription():
    """Test subscribing with a valid email."""
    print("\n" + "=" * 60)
    print("TEST 1: Valid Email Subscription")
    print("=" * 60)

    data = {"email": "user1@example.com"}

    response = requests.post(f"{BASE_URL}/subscribe/", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")

    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    result = response.json()
    assert result["success"] is True
    assert "Successfully subscribed" in result["message"]
    assert result["data"]["email"] == "user1@example.com"

    print("✓ Test passed!")
    return result["data"]["id"]


def test_duplicate_subscription():
    """Test subscribing with an already registered email."""
    print("\n" + "=" * 60)
    print("TEST 2: Duplicate Email Subscription")
    print("=" * 60)

    data = {"email": "user1@example.com"}

    response = requests.post(f"{BASE_URL}/subscribe/", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")

    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    result = response.json()
    assert "Already subscribed" in result["error"]

    print("✓ Test passed!")


def test_invalid_email_format():
    """Test subscribing with invalid email format."""
    print("\n" + "=" * 60)
    print("TEST 3: Invalid Email Format")
    print("=" * 60)

    data = {"email": "not-an-email"}

    response = requests.post(f"{BASE_URL}/subscribe/", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")

    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    result = response.json()
    assert "email" in result

    print("✓ Test passed!")


def test_missing_email_field():
    """Test subscribing without email field."""
    print("\n" + "=" * 60)
    print("TEST 4: Missing Email Field")
    print("=" * 60)

    data = {}

    response = requests.post(f"{BASE_URL}/subscribe/", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")

    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    result = response.json()
    assert "email" in result

    print("✓ Test passed!")


def test_empty_email():
    """Test subscribing with empty email."""
    print("\n" + "=" * 60)
    print("TEST 5: Empty Email")
    print("=" * 60)

    data = {"email": ""}

    response = requests.post(f"{BASE_URL}/subscribe/", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")

    assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    print("✓ Test passed!")


def test_case_insensitive_email():
    """Test that emails are case-insensitive."""
    print("\n" + "=" * 60)
    print("TEST 6: Case-Insensitive Email")
    print("=" * 60)

    # Subscribe with lowercase
    data1 = {"email": "user2@example.com"}
    response1 = requests.post(f"{BASE_URL}/subscribe/", json=data1)
    print(f"Lowercase subscription - Status: {response1.status_code}")

    assert response1.status_code == 201

    # Try to subscribe with uppercase (should fail as duplicate)
    data2 = {"email": "USER2@EXAMPLE.COM"}
    response2 = requests.post(f"{BASE_URL}/subscribe/", json=data2)
    print(f"Uppercase subscription - Status: {response2.status_code}")
    print(f"Response:\n{json.dumps(response2.json(), indent=2)}")

    assert response2.status_code == 400, f"Expected 400, got {response2.status_code}"

    print("✓ Test passed! Emails are properly normalized.")


def test_whitespace_handling():
    """Test that whitespace is trimmed from emails."""
    print("\n" + "=" * 60)
    print("TEST 7: Whitespace Handling")
    print("=" * 60)

    data = {"email": "  user3@example.com  "}

    response = requests.post(f"{BASE_URL}/subscribe/", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")

    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    result = response.json()
    # Email should be trimmed
    assert result["data"]["email"] == "user3@example.com"

    print("✓ Test passed! Whitespace is properly trimmed.")


def test_multiple_valid_subscriptions():
    """Test subscribing multiple different emails."""
    print("\n" + "=" * 60)
    print("TEST 8: Multiple Valid Subscriptions")
    print("=" * 60)

    emails = [
        "alice@example.com",
        "bob@example.com",
        "charlie@example.com",
    ]

    for email in emails:
        data = {"email": email}
        response = requests.post(f"{BASE_URL}/subscribe/", json=data)
        print(f"{email} - Status: {response.status_code}")

        assert (
            response.status_code == 201
        ), f"Expected 201 for {email}, got {response.status_code}"

    print("✓ Test passed! All subscriptions successful.")


def test_special_characters_in_email():
    """Test emails with special characters."""
    print("\n" + "=" * 60)
    print("TEST 9: Special Characters in Email")
    print("=" * 60)

    # Valid email with special characters
    data = {"email": "user+test@example.com"}

    response = requests.post(f"{BASE_URL}/subscribe/", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")

    assert response.status_code == 201, f"Expected 201, got {response.status_code}"

    print("✓ Test passed!")


def test_long_email():
    """Test email with maximum allowed length."""
    print("\n" + "=" * 60)
    print("TEST 10: Long Email Address")
    print("=" * 60)

    # Create a long but valid email (under 255 chars)
    long_name = "a" * 50
    data = {"email": f"{long_name}@example.com"}

    response = requests.post(f"{BASE_URL}/subscribe/", json=data)
    print(f"Status: {response.status_code}")
    print(f"Email length: {len(data['email'])} characters")

    if response.status_code == 201:
        print("✓ Test passed! Long email accepted.")
    else:
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("NEWSLETTER SUBSCRIPTION API TESTS")
    print("=" * 60)
    print("\nMake sure the Django server is running on http://localhost:8000")
    input("Press Enter to start tests...")

    try:
        # Run tests
        subscriber_id = test_valid_subscription()
        test_duplicate_subscription()
        test_invalid_email_format()
        test_missing_email_field()
        test_empty_email()
        test_case_insensitive_email()
        test_whitespace_handling()
        test_multiple_valid_subscriptions()
        test_special_characters_in_email()
        test_long_email()

        # Summary
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print(f"\nFirst subscriber ID: {subscriber_id}")
        print("\nNewsletter Subscription feature is working correctly!")
        print("\nYou can now:")
        print("  1. Subscribe at: POST http://localhost:8000/api/subscribe/")
        print("  2. Check Django Admin for subscriber list")
        print("  3. Integrate with your frontend form")

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Make sure Django server is running: python manage.py runserver")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
