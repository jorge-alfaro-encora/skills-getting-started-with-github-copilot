"""
Comprehensive API tests for activities endpoints
Using AAA (Arrange-Act-Assert) pattern
"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client, mock_activities):
        """Happy path: Should return all activities with participants"""
        # Arrange
        expected_activity_count = 9
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert len(response.json()) == expected_activity_count
        assert "Chess Club" in response.json()
        assert "Programming Class" in response.json()

    def test_get_activities_includes_correct_details(self, client, mock_activities):
        """Happy path: Should return complete activity information"""
        # Arrange
        expected_keys = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        chess_club = activities["Chess Club"]
        assert all(key in chess_club for key in expected_keys)
        assert chess_club["max_participants"] == 12
        assert "michael@mergington.edu" in chess_club["participants"]

    def test_get_activities_participants_list_is_not_empty(self, client, mock_activities):
        """Happy path: Should include participants in activities"""
        # Arrange
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        # Check that at least some activities have participants
        activities_with_participants = [
            a for a in activities.values() if len(a["participants"]) > 0
        ]
        assert len(activities_with_participants) > 0


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_happy_path(self, client, mock_activities):
        """Happy path: Student successfully signs up for activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "new_student@mergington.edu"
        initial_count = len(mock_activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in mock_activities[activity_name]["participants"]
        assert len(mock_activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_for_nonexistent_activity(self, client, mock_activities):
        """Error case: Should return 404 when activity doesn't exist"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_student(self, client, mock_activities):
        """Error case: Should prevent duplicate signups"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"

    def test_signup_multiple_students_same_activity(self, client, mock_activities):
        """Happy path: Multiple different students can sign up"""
        # Arrange
        activity_name = "Programming Class"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email1 in mock_activities[activity_name]["participants"]
        assert email2 in mock_activities[activity_name]["participants"]

    def test_signup_same_student_different_activities(self, client, mock_activities):
        """Happy path: Same student can sign up for multiple activities"""
        # Arrange
        email = "versatile_student@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Art Studio"
        
        # Act
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email in mock_activities[activity1]["participants"]
        assert email in mock_activities[activity2]["participants"]

    def test_signup_with_special_characters_in_email(self, client, mock_activities):
        """Edge case: Handle email with special characters"""
        # Arrange
        activity_name = "Gym Class"
        email = "student+tag@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in mock_activities[activity_name]["participants"]

    def test_signup_activity_name_case_sensitive(self, client, mock_activities):
        """Edge case: Activity names should be case-sensitive"""
        # Arrange
        activity_name = "chess club"  # lowercase
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_happy_path(self, client, mock_activities):
        """Happy path: Student successfully unregisters from activity"""
        # Arrange
        activity_name = "Tennis Club"
        email = "sarah@mergington.edu"  # Already signed up
        initial_count = len(mock_activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in mock_activities[activity_name]["participants"]
        assert len(mock_activities[activity_name]["participants"]) == initial_count - 1

    def test_unregister_from_nonexistent_activity(self, client, mock_activities):
        """Error case: Should return 404 when activity doesn't exist"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_student_not_in_activity(self, client, mock_activities):
        """Error case: Should return 404 when student is not registered"""
        # Arrange
        activity_name = "Chess Club"
        email = "not_signed_up@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Student not found in activity"

    def test_unregister_twice_same_student(self, client, mock_activities):
        """Edge case: Should prevent double unregistration"""
        # Arrange
        activity_name = "Music Band"
        email = "david@mergington.edu"
        
        # Act - First unregister (should succeed)
        response1 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        # Second unregister attempt (should fail)
        response2 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 404
        assert response2.json()["detail"] == "Student not found in activity"

    def test_unregister_then_signup_again(self, client, mock_activities):
        """Happy path: Student can re-register after unregistering"""
        # Arrange
        activity_name = "Debate Club"
        email = "rachel@mergington.edu"
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        # Re-register
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert unregister_response.status_code == 200
        assert signup_response.status_code == 200
        assert email in mock_activities[activity_name]["participants"]

    def test_unregister_multiple_participants(self, client, mock_activities):
        """Happy path: Unregister one student doesn't affect others"""
        # Arrange
        activity_name = "Science Club"
        email_to_remove = "marcus@mergington.edu"
        other_email = "nina@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )
        
        # Assert
        assert response.status_code == 200
        assert email_to_remove not in mock_activities[activity_name]["participants"]
        assert other_email in mock_activities[activity_name]["participants"]

    def test_unregister_activity_name_case_sensitive(self, client, mock_activities):
        """Edge case: Activity names should be case-sensitive on unregister"""
        # Arrange
        activity_name = "tennis club"  # lowercase
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404


class TestIntegrationScenarios:
    """Integration tests for complete workflows"""

    def test_signup_unregister_signup_workflow(self, client, mock_activities):
        """Integration: Complete lifecycle of signup, unregister, signup again"""
        # Arrange
        activity_name = "Art Studio"
        email = "new_artist@mergington.edu"
        
        # Act & Assert - Sign up
        signup1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup1.status_code == 200
        participants_after_signup1 = len(mock_activities[activity_name]["participants"])
        
        # Unregister
        unregister = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert unregister.status_code == 200
        participants_after_unregister = len(mock_activities[activity_name]["participants"])
        assert participants_after_signup1 - 1 == participants_after_unregister
        
        # Sign up again
        signup2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup2.status_code == 200
        assert email in mock_activities[activity_name]["participants"]

    def test_multiple_concurrent_student_signups(self, client, mock_activities):
        """Integration: Multiple students signing up for same activity"""
        # Arrange
        activity_name = "Basketball Team"
        new_students = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        # Act
        responses = []
        for email in new_students:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            responses.append(response)
        
        # Assert
        assert all(r.status_code == 200 for r in responses)
        for email in new_students:
            assert email in mock_activities[activity_name]["participants"]
        
        # Verify total count
        expected_count = 1 + len(new_students)  # 1 existing (james) + 3 new
        assert len(mock_activities[activity_name]["participants"]) == expected_count
