# streamlit-auth0-service
Service to authorize user by checking the `token` in the param variable of the streamlit page URL.

## Environment Variables
* AUTH0_CLAIM_KEY: JWT claim key that holds `user_metadata.org`.
* AUTH0_DOMAIN: Auth0 domain name that verifies the access token.
* ORG_ID: (Optional) organization ID. If provided, limits the access to the provided organization's users only.

## Usage

* install the dependency:
```shell
pip install streamlit-auth0-service==0.0.9
```

* Use `@authorized` in the method that need to be authorized.

```python
from atlasai.streamlit.auth.guard import authorized
import streamlit as st


@authorized
def run():
    st.write("You must be Authorized to see this content")


if __name__ == '__main__':
    run()
```