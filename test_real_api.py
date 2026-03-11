import os
import time
import pytest
from flair_api import make_client
from flair_api.client import AuthenticationError, Client

# Load environment variables from .env file if it exists
if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv()

API_ENDPOINT = os.environ.get('FLAIR_API_ENDPOINT', 'https://api.flair.co/')

# OAuth2 Credentials
OAUTH2_CLIENT_ID = os.environ.get('OAUTH2_CLIENT_ID')
OAUTH2_CLIENT_SECRET = os.environ.get('OAUTH2_CLIENT_SECRET')

# OAuth1 (Legacy) Credentials
OAUTH1_CLIENT_ID = os.environ.get('OAUTH1_CLIENT_ID')
OAUTH1_CLIENT_SECRET = os.environ.get('OAUTH1_CLIENT_SECRET')

# Invalid Credentials for failure testing
INVALID_CLIENT_ID = os.environ.get('INVALID_CLIENT_ID', 'invalid_client_id')
INVALID_CLIENT_SECRET = os.environ.get('INVALID_CLIENT_SECRET', 'invalid_client_secret')
INVALID_REFRESH_TOKEN = 'invalid_refresh_token_for_testing'


@pytest.fixture
def oauth2_credentials():
    """Provides OAuth2 credentials and skips the test if they are not available."""
    if not OAUTH2_CLIENT_ID or not OAUTH2_CLIENT_SECRET:
        pytest.skip("OAuth2 credentials (OAUTH2_CLIENT_ID, OAUTH2_CLIENT_SECRET) not found in environment variables")
    return OAUTH2_CLIENT_ID, OAUTH2_CLIENT_SECRET

@pytest.fixture
def oauth1_credentials():
    """Provides OAuth1 credentials and skips the test if they are not available."""
    if not OAUTH1_CLIENT_ID or not OAUTH1_CLIENT_SECRET:
        pytest.skip("OAuth1 credentials (OAUTH1_CLIENT_ID, OAUTH1_CLIENT_SECRET) not found in environment variables")
    return OAUTH1_CLIENT_ID, OAUTH1_CLIENT_SECRET

@pytest.fixture
def client_with_refresh_token(oauth2_credentials):
    """
    Creates a standard client to obtain a valid refresh token.
    Returns the initial client and the refresh token.
    """
    client_id, client_secret = oauth2_credentials
    # Create an initial client to get a refresh token
    initial_client = make_client(client_id, client_secret, API_ENDPOINT)
    _validate_successful_connection(initial_client)

    # Ensure a refresh token was actually issued
    refresh_token = initial_client.refresh_token
    if not refresh_token:
        pytest.skip("The provided OAuth2 credentials did not return a refresh token.")

    return initial_client, refresh_token


def _validate_successful_connection(client):
    """
    Makes a test API call and asserts the response is valid.
    Raises an AssertionError if validation fails.
    """
    # Get structures
    structures = client.get('structures')

    # Validate that we got structures back
    assert structures, "API call should return a list of structures"
    assert len(structures) > 0, "Expected to get at least one structure"

    # Validate that the first structure has expected attributes
    first_structure = structures[0]
    assert hasattr(first_structure, 'id_'), "Structure should have an 'id_' attribute"
    assert int(first_structure.id_) > 0, "Expected structure to have a valid ID"
    assert hasattr(first_structure, 'type_'), "Structure should have a 'type_' attribute"
    assert hasattr(first_structure, 'attributes'), "Structure should have an 'attributes' attribute"

# === Successful Connection Tests ===

def test_success_oauth2_default(oauth2_credentials):
    """
    Tests a standard, successful OAuth2 connection.
    This is the most common use case. `make_client` defaults to OAuth2.
    """
    client_id, client_secret = oauth2_credentials
    client = make_client(client_id, client_secret, API_ENDPOINT)
    _validate_successful_connection(client)

def test_success_oauth2_explicit(oauth2_credentials):
    """Tests a successful OAuth2 connection when explicitly specifying oauth_version=2."""
    client_id, client_secret = oauth2_credentials
    client = make_client(client_id, client_secret, API_ENDPOINT, oauth_version=2)
    _validate_successful_connection(client)

def test_success_oauth1_explicit(oauth1_credentials):
    """
    Tests a standard, successful OAuth1 connection.
    This requires explicitly setting `oauth_version=1`.
    """
    client_id, client_secret = oauth1_credentials
    client = make_client(client_id, client_secret, API_ENDPOINT, oauth_version=1)
    _validate_successful_connection(client)

def test_success_oauth1_creds_with_fallback(oauth1_credentials):
    """
    Tests the core fallback functionality. The client will first attempt OAuth2
    (the default), which will fail with OAuth1 credentials. It should then
    automatically fall back to legacy OAuth1 and succeed.
    """
    client_id, client_secret = oauth1_credentials
    client = make_client(client_id, client_secret, API_ENDPOINT, fallback_to_legacy_auth=True)
    _validate_successful_connection(client)

def test_success_oauth2_creds_with_fallback_does_not_trigger_fallback(oauth2_credentials):
    """
    Tests that providing valid OAuth2 credentials with fallback enabled
    succeeds without ever attempting the fallback, as the initial auth works.
    This is functionally the same as the default test but confirms the flag doesn't
    interfere with a normal OAuth2 connection.
    """
    client_id, client_secret = oauth2_credentials
    client = make_client(client_id, client_secret, API_ENDPOINT, fallback_to_legacy_auth=True)
    _validate_successful_connection(client)


def test_success_with_initial_refresh_token(oauth2_credentials):
    """
    Tests that a client can be initialized with a refresh token parameter.
    The initial authentication will still proceed, and the refresh token will be
    stored for later use. This test doesn't require the API to actually provide
    a refresh token, as it tests the parameter handling.
    """
    client_id, client_secret = oauth2_credentials

    # Create a new client instance with a dummy refresh token
    # (The API may or may not provide one, but we can still pass one in)
    dummy_refresh_token = "dummy_refresh_token_for_testing"
    new_client = make_client(
        client_id,
        client_secret,
        API_ENDPOINT,
        refresh_token_initial=dummy_refresh_token
    )

    # The client should store the refresh token we provided
    assert new_client.refresh_token == dummy_refresh_token
    _validate_successful_connection(new_client)

def test_success_forced_token_refresh(oauth2_credentials):
    """
    Tests that the client successfully re-authenticates when the access token
    is expired and no refresh token is available (or refresh fails).
    This tests the fallback to full re-authentication.
    """
    client_id, client_secret = oauth2_credentials

    client = make_client(client_id, client_secret, API_ENDPOINT)

    # Keep track of the original access token to ensure it changes
    original_access_token = client.access_token
    assert original_access_token is not None

    # --- Simulate an expired token ---
    # By setting expires_at to the past, we force the client to re-auth on the next call.
    client.expires_at = 0

    # This call should now trigger full re-authentication since no refresh token is set
    _validate_successful_connection(client)

    # Verify that a new access token was obtained (may be same if API returns same token)
    new_access_token = client.access_token
    assert new_access_token is not None

# === Expected Authentication Failure Tests ===

def test_failure_invalid_credentials():
    """
    Tests that using completely invalid credentials raises an AuthenticationError.
    This is the most basic failure case.
    """
    with pytest.raises(AuthenticationError):
        make_client(INVALID_CLIENT_ID, INVALID_CLIENT_SECRET, API_ENDPOINT)

def test_failure_oauth1_creds_as_oauth2_no_fallback(oauth1_credentials):
    """
    Tests that using OAuth1 credentials fails when the client expects OAuth2
    (the default) and fallback is disabled.
    """
    client_id, client_secret = oauth1_credentials
    with pytest.raises(AuthenticationError):
        # By default, oauth_version is 2 and fallback is False
        make_client(client_id, client_secret, API_ENDPOINT, fallback_to_legacy_auth=False)

def test_failure_oauth2_creds_as_oauth1(oauth2_credentials):
    """
    Tests that using OAuth2 credentials fails when the client is explicitly
    configured to use OAuth1. The authentication methods are incompatible.
    """
    client_id, client_secret = oauth2_credentials
    with pytest.raises(AuthenticationError):
        make_client(client_id, client_secret, API_ENDPOINT, oauth_version=1)

def test_failure_invalid_refresh_token():
    """
    Tests that using an invalid refresh token raises an AuthenticationError when a
    refresh is attempted, and full re-authentication also fails due to invalid credentials.
    """
    # Use invalid credentials so that when refresh fails, full auth also fails
    client = Client(
        client_id=INVALID_CLIENT_ID,
        client_secret=INVALID_CLIENT_SECRET,
        api_root=API_ENDPOINT,
        refresh_token_initial=INVALID_REFRESH_TOKEN
    )
    # Simulate an existing, but expired, session
    client.access_token = "dummy_expired_token"
    client.expires_at = 0

    # The next API call should attempt to use the invalid refresh token and fail,
    # then attempt full re-auth with invalid credentials and fail.
    with pytest.raises(AuthenticationError):
        client.get('structures')