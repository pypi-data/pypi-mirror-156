import os

import requests
import streamlit as st
import logging

# from dotenv import load_dotenv
# load_dotenv('.env')

AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']
AUTH0_CLAIM_KEY = os.environ['AUTH0_CLAIM_KEY']
ORG_ID = os.environ.get('ORG_ID')


class StreamlitAuth0Service:

    def __init__(self):
        self.issuer_url = f'https://{AUTH0_DOMAIN}/'
        self.user_info_uri = f'{self.issuer_url}userinfo'


    def is_authorized(self, org_id="") -> bool:
        # Check user in the session
        if 'user' in st.session_state:
            session_user_authorized = self.is_session_user_authorized(org_id)
            if session_user_authorized:
                logging.info("is_authorized: Valid user session found.")
                return True
            else:
                logging.info("is_authorized: Unauthorized user session! Requesting user info from auth service.")
        else:
            logging.info("is_authorized: No valid user session found. Requesting user info from auth service.")

        # authorize user through token param
        token = self.get_token()
        if token is None:
            return False
        else:
            user = self.get_user_info(token)
            return self.is_authorized_user(user, org_id)


    # Checks if provided user is authorized.
    def is_authorized_user(self, user, org_id="") -> bool:
        org_id = self.get_org_id(org_id)
        if org_id is not None and len(org_id) > 0:
            return (user is not None
                    and user[AUTH0_CLAIM_KEY] is not None
                    and user[AUTH0_CLAIM_KEY]["user_metadata"]["org"] == org_id)
        else:
            return user is not None and user["email"] is not None


    # Gets user info from Auth service through API call using user's access token
    def get_user_info(self, bearer_token: str) -> object:
        logging.info("is_authorized: Getting user info from Auth Service.")
        try:
            headers = {'Authorization': f'Bearer {bearer_token}'}
            response = requests.get(self.user_info_uri, headers=headers)
        except Exception as e:
            logging.info('Error getting user info: ', e)
            return None

        if response.status_code != 200:
            logging.info('Error response from Auth Service: ', response)
            return None

        self.save_user_session(response.json())
        return response.json()


    # Saves the given user in the session
    def save_user_session(self, user):
        # Save user in session
        if user is not None:
            logging.info("is_authorized: Saving user in session")
            st.session_state['user'] = user
        else:
            logging.info("is_authorized: User is None and cannot be saved in the session")


    # Checks if the user in the session is authorized
    def is_session_user_authorized(self, org_id):
        return self.is_authorized_user(st.session_state['user'], org_id)


    # Gets organization's ID either from given param or from Environment variable.
    def get_org_id(self, org_id) -> str:
        if org_id is None or len(org_id) == 0:
            return ORG_ID
        else:
            return org_id


    # Gets user token value from query param in the url.
    def get_token(self) -> str:
        query_params = st.experimental_get_query_params()
        token_array = query_params.get('token')
        if token_array is None or len(token_array) < 1:
            logging.info("is_authorized: Auth Token not found in the query param!")
            return None
        else:
            logging.info("is_authorized: Auth Token found in the query param.")
            return token_array[0]
