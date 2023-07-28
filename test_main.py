from main import User
from main import UserLoginData
from main import UserSurveyData
from main import app
from main import session
from fastapi.testclient import TestClient
import pytest


client = TestClient(app)

newUser = User(
    username="testuser",
    password="Testpass",
    email="TestEmail",
    firstName="TestFname")
if (len(session.query(User).filter(
    User.username == newUser.username
).all()) == 0):
    session.add(newUser)
    session.commit()


@pytest.mark.api
def test_remove_test_cases():
    response = client.put("/removetests")
    assert response.status_code == 200


@pytest.mark.api
def test_add_user():
    # Test case: create a new user
    data = UserLoginData(
        username="testuser",
        password="Testpass",
        email="TestEmailmain",
        firstName="TestFname")
    response = client.put("/addUser", json=data.__dict__)
    assert response.status_code == 200
    assert response.json() == {"detail": "Succ"}


@pytest.mark.api
def test_overlapping_email():
    # Test case: create user with duplicate email
    data = UserLoginData(
        username="testuser1",
        password="Testpass1",
        email="TestEmailmain",
        firstName="TestFname1")
    response = client.put("/addUser", json=data.__dict__)
    assert response.status_code == 400
    assert response.json() == {"detail": "double email"}


@pytest.mark.api
def test_overlapping_user():
    # Test case: create user with duplicate username
    data = UserLoginData(
        username="testuser",
        password="Testpass1",
        email="TestEmail1",
        firstName="TestFname1")
    response = client.put("/addUser", json=data.__dict__)
    assert response.status_code == 400
    assert response.json() == {"detail": "double user"}


@pytest.mark.api
def test_username_case_duplicate_handling():
    # Test case: create user with same name as another -different case
    # letters- to test case sensitivity
    data = UserLoginData(
        username="tEsTuSeR",
        password="Testpass2",
        email="TestEmail2",
        firstName="TestFname2")
    response = client.put("/addUser", json=data.__dict__)
    assert response.status_code == 400
    assert response.json() == {"detail": "double user"}


@pytest.mark.api
def test_password_duplicate():
    # Test case: create user with password duplicate
    data = UserLoginData(
        username="testuser3",
        password="Testpass",
        email="TestEmail3",
        firstName="TestFname3")
    response = client.put("/addUser", json=data.__dict__)
    assert response.status_code == 200
    assert response.json() == {"detail": "Succ"}


@pytest.mark.api
def test_firstName_duplicate():
    # Test case: create user with a firstName field duplicate
    data = UserLoginData(
        username="testuser4",
        password="Testpass4",
        email="TestEmail4",
        firstName="TestFname")
    response = client.put("/addUser", json=data.__dict__)
    assert response.status_code == 200
    assert response.json() == {"detail": "Succ"}


@pytest.mark.api
def test_putUserSurveyData():
    # Test case: create user survey with all values entered
    data = UserSurveyData(
        userID=67,
        calorie_goal="2",
        gender="male",
        height="3",
        weight="4",
        age="5",
        cooking_exp="new",
        num_days="1",
        activity_level="some")
    response = client.put("/userSurveyData", json=data.__dict__)
    assert response.status_code == 200


@pytest.mark.api
def test_putUserSurveyDataEmptyVals():
    # Test case: create user survey with all empty values
    data = UserSurveyData(
        userID=67,
        calorie_goal="",
        gender="",
        height="",
        weight="",
        age="",
        cooking_exp="",
        num_days="",
        activity_level="")
    response = client.put("/userSurveyData", json=data.__dict__)
    assert response.status_code == 200


@pytest.mark.api
def test_searchRecipesTitleEmpty():
    # Test case: search with an empty search value
    response = client.get("/recipes/searchtitle/")
    assert response.status_code == 200


@pytest.mark.api
def test_searchRecipesTitle():
    # Test case: search with a search value containing records
    response = client.get("/recipes/searchtitle/carrot")
    assert response.status_code == 200


@pytest.mark.api
def test_searchRecipesTitleNoRecords():
    # Test case: search with a search value containing records
    response = client.get("/recipes/searchtitle/nonexistentrecord")
    assert response.status_code == 200


@pytest.mark.api
def test_searchRecipesTagEmpty():
    # Test case: search with an empty search value
    response = client.get("/recipes/searchtags/")
    assert response.status_code == 200


@pytest.mark.api
def test_searchRecipesTag():
    # Test case: search with a search value containing records
    response = client.get("/recipes/searchtags/oven")
    assert response.status_code == 200


@pytest.mark.api
def test_searchRecipesTagNoRecords():
    # Test case: search with a search value containing records
    response = client.get("/recipes/searchtags/nonexistentrecord")
    assert response.status_code == 200
