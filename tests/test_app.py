import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module

BASE_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
}

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities = copy.deepcopy(BASE_ACTIVITIES)
    yield


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()

    assert "Chess Club" in data
    assert data["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_for_activity():
    response = client.post(
        "/activities/Chess%20Club/signup?email=alex@mergington.edu"
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Signed up alex@mergington.edu for Chess Club"
    assert "alex@mergington.edu" in app_module.activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael@mergington.edu"
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already registered"


def test_unregister_participant_from_activity():
    response = client.delete(
        "/activities/Chess%20Club/participants?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"
    assert app_module.activities["Chess Club"]["participants"] == ["daniel@mergington.edu"]


def test_unregister_missing_participant_returns_404():
    response = client.delete(
        "/activities/Chess%20Club/participants?email=unknown@mergington.edu"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
