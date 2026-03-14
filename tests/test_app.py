from fastapi.testclient import TestClient
import pytest

from src.app import app


@pytest.fixture
def client():
    return TestClient(app, follow_redirects=False)


def test_root_redirect(client):
    # Arrange - TestClient is set up

    # Act - Make GET request to root
    response = client.get("/")

    # Assert - Should redirect to static index
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    # Arrange - TestClient is set up

    # Act - Make GET request to activities
    response = client.get("/activities")

    # Assert - Should return 200 and activities data
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0  # Should have activities
    # Check structure of one activity
    activity = next(iter(data.values()))
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_signup_success(client):
    # Arrange - Get initial state
    initial_response = client.get("/activities")
    initial_data = initial_response.json()
    activity_name = "Chess Club"
    initial_participants = len(initial_data[activity_name]["participants"])
    email = "test@example.com"

    # Act - Signup for activity
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert - Should succeed and add participant
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    # Verify participant was added
    after_response = client.get("/activities")
    after_data = after_response.json()
    assert len(after_data[activity_name]["participants"]) == initial_participants + 1
    assert email in after_data[activity_name]["participants"]


def test_signup_activity_not_found(client):
    # Arrange - Use non-existent activity
    activity_name = "Nonexistent Activity"
    email = "test@example.com"

    # Act - Attempt signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert - Should return 404
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_already_signed_up(client):
    # Arrange - First signup
    activity_name = "Chess Club"
    email = "test@example.com"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act - Attempt second signup with same email
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert - Should return 400
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up"}