import pytest
import pandas as pd
import uuid
from src.database import init_db, create_user, authenticate_user, save_analysis, get_user_sessions, get_session_comments, get_db_connection

@pytest.fixture(scope="module")
def db_setup():
    init_db()
    yield

def test_user_creation_and_auth(db_setup):
    unique_username = f"test_user_{uuid.uuid4().hex[:8]}"
    password = "supersecretpassword"
    
    # Create user
    user = create_user(unique_username, password)
    assert user["username"] == unique_username
    assert user["role"] == "general"
    
    # Authenticate successfully
    auth_user = authenticate_user(unique_username, password)
    assert auth_user is not None
    assert auth_user["user_id"] == user["user_id"]
    assert auth_user["username"] == unique_username
    assert auth_user["role"] == "general"
    
    # Fail authentication
    assert authenticate_user(unique_username, "wrongpassword") is None
    
    # Try duplicate username
    with pytest.raises(ValueError, match="Username already exists"):
        create_user(unique_username, "anypassword")

def test_save_analysis_batch(db_setup):
    unique_username = f"test_user_{uuid.uuid4().hex[:8]}"
    user = create_user(unique_username, "password")
    user_id = user["user_id"]
    
    url = "https://facebook.com/posts/test_batch"
    
    # Create a dummy DataFrame with texts, sentiment, and timestamp
    df = pd.DataFrame([
        {"text": "Chichewa is a beautiful language", "predicted_sentiment": "positive", "created_at": "2026-06-29T14:00:00Z"},
        {"text": "Zinthu sizikuyenda bwino", "predicted_sentiment": "negative", "created_at": "2026-06-29T14:15:00Z"},
        {"text": "Ndili bwino zikomo", "predicted_sentiment": "neutral", "created_at": "2026-06-29T14:30:00Z"}
    ])
    
    # Save analysis
    session = save_analysis(user_id, url, df)
    assert session is not None
    assert session["url"] == url
    
    # Verify session is fetched
    sessions = get_user_sessions(user_id)
    assert len(sessions) == 1
    assert sessions[0]["session_id"] == session["session_id"]
    
    # Verify comments are fetched
    comments = get_session_comments(session["session_id"])
    assert len(comments) == 3
    
    # Check details of comments
    comments_df = pd.DataFrame(comments)
    assert "Chichewa is a beautiful language" in comments_df["comment_text"].values
    assert "positive" in comments_df["sentiment_label"].values
    assert pd.notna(comments_df["created_time"]).all()

def test_session_title_renaming(db_setup):
    unique_username = f"test_user_{uuid.uuid4().hex[:8]}"
    user = create_user(unique_username, "password")
    user_id = user["user_id"]
    
    from src.database import create_session, update_session_title, get_session
    session = create_session(user_id, "https://facebook.com/posts/test_rename")
    assert session["custom_title"] is None
    
    # Update title
    update_session_title(session["session_id"], "New Session Title")
    updated = get_session(session["session_id"])
    assert updated["custom_title"] == "New Session Title"
    
    # Reset title
    update_session_title(session["session_id"], None)
    reset_sess = get_session(session["session_id"])
    assert reset_sess["custom_title"] is None

def test_session_deletion_cascade(db_setup):
    unique_username = f"test_user_{uuid.uuid4().hex[:8]}"
    user = create_user(unique_username, "password")
    user_id = user["user_id"]
    
    from src.database import delete_session, get_session
    
    df = pd.DataFrame([
        {"text": "Comment 1", "predicted_sentiment": "positive", "created_at": "2026-06-29T14:00:00Z"},
        {"text": "Comment 2", "predicted_sentiment": "negative", "created_at": "2026-06-29T14:15:00Z"}
    ])
    
    session = save_analysis(user_id, "https://facebook.com/posts/test_delete", df)
    session_id = session["session_id"]
    
    # Assert exist
    assert get_session(session_id) is not None
    assert len(get_session_comments(session_id)) == 2
    
    # Delete session
    delete_session(session_id)
    
    # Assert session is gone
    assert get_session(session_id) is None
    # Assert comments are gone (cascade)
    assert len(get_session_comments(session_id)) == 0
