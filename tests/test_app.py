from pathlib import Path
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app import app, activities  # noqa: E402

client = TestClient(app)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_prevent_duplicate():
    email = "pytest_student@mergington.edu"
    activity = "Chess Club"

    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 200
    assert email in activities[activity]["participants"]

    dup_response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert dup_response.status_code == 400

    activities[activity]["participants"].remove(email)


def test_remove_participant():
    email = "pytest_remove@mergington.edu"
    activity = "Programming Class"

    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)

    response = client.delete(f"/activities/{activity}/participants/{email}")
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_remove_participant_not_found():
    email = "not_in_list@mergington.edu"
    activity = "Gym Class"

    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    response = client.delete(f"/activities/{activity}/participants/{email}")
    assert response.status_code == 404
