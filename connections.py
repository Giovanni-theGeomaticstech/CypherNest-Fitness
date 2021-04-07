"""
This file will focus on making our connection to the Backend
"""

import requests
import json
import uuid

# User Based Functions
def registration(username: str, email: str, password: str, firstname: str, lastname: str) -> requests:
    """ User Registration """
    request_info = requests.post(
        "https://cypher-fitness-app.herokuapp.com/api/register/",
        data={"username": username,
              "firstname": firstname,
              "lastname": lastname,
              "email": email,
              "password": password},
    )
    # Note I can get the status_code
    # .json() would give me the
    # {user:{}, token;{}}
    return request_info


# We pass the token information into the user_data function
def login(username: str, password: str) -> str:
    """ Login in to the System
    Return:
         the successful token if the user exists
         None if unsuccessful
    """
    # https://cypher-fitness-app.herokuapp.com/api/login/
    request_info = requests.post(
        "https://cypher-fitness-app.herokuapp.com/api/login/",
        data={"username": username, "password": password},
    )
    if request_info.status_code == 200:
        return request_info.json()["token"]
    return None


def logout(token: str) -> str:
    """ Logout from the System
    Parameter:
        token -> From the login
    """
    header = {"Authorization": f"Token {token}"}  # Build the authorization header
    request_info = requests.get("https://cypher-fitness-app.herokuapp.com/api/logout/", headers=header)
    return request_info


def logout_all(token: str) -> str:
    """ Login out all accounts from the System
    Parameter:
        token -> From the login
    """
    header = {"Authorization": f"Token {token}"}  # Build the authorization header
    request_info = requests.get("https://cypher-fitness-app.herokuapp.com/api/logout-all/", headers=header)
    return request_info


def user_data(token: str) -> json:
    """ Get A Single User"""
    header = {"Authorization": f"Token {token}"}  # Build the authorization header
    request_info = requests.get("https://cypher-fitness-app.herokuapp.com/api/user/", headers=header)
    return request_info.json()  # user info


def user_list() -> list:
    """ List All the Users in the System
    # Maybe need restrictions so that super users are not chosen

    Return is a list of Dicts
    """

    request_info = requests.get("https://cypher-fitness-app.herokuapp.com/api/user_list/")

    return request_info.json()


# Journey Based Functions


def create_journey_json(data: list, speed=[], altitude=[],
                        time=[], bearing=[]) -> json:
    """ Making the GeoJSON OBJECT FOR OUR JOURNEY"""

    properties = {
            "speed": speed,
            "time": time,
            "altitude": altitude,
            "bearing": bearing
        }
    if not speed:
        geojson_obj = {
            "geometry": {
                "type": "LineString",
                "coordinates": data}  # Coordinates
        }
    else:
        geojson_obj = {
            "properties":properties,
            "geometry": {
                "type": "LineString",
                "coordinates": data}  # Coordinates
        }
    return geojson_obj


def journey_post(data: list, speed: list, altitude: list, time: list, bearing: list,
                 token: str) -> requests:
    """ Adding a new Journey to the database"""
    journey = create_journey_json(data, speed, altitude, time, bearing)
    journey_json = json.dumps(journey)  # When I edit the view use this
    user = user_data(token)
    request_info = requests.post(
        "https://cypher-fitness-app.herokuapp.com/api/new_journey/",
        data={"feature_info": journey_json, "user_profile": user["id"]},
    )
    return request_info


def journey_list(user_id: int) -> list:
    """ Here We get the list of Journey's for a user
    Parameters:
        id: A user id
    Return is a list of Dicts
    """

    # user = user_data(token)
    request_info = requests.get(f"https://cypher-fitness-app.herokuapp.com/api/journey_list/{user_id}")
    return request_info.json()


def retrieve_journey(id: uuid):
    """ Retrieve a Journey for one User
    We use this for when we choose a journey from a journey list
    Parameters:
        id: unique_field (uuid) of a journey
    Returns a Journey
    """

    request_info = requests.get(f"https://cypher-fitness-app.herokuapp.com/api/retrieve_journey/{id}")

    return request_info.json()
