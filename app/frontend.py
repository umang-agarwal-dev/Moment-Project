import streamlit as st
import requests
import base64
import urllib.parse

st.set_page_config(page_title="Simple Social", page_icon="🚀", layout="wide")

# ---------------------------------------------------------------------------
# Global styling
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        max-width: 900px;
    }
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: transform 0.05s ease-in-out;
    }
    .stButton > button:active { transform: scale(0.98); }

    .post-card {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1.4rem;
    }
    .post-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.6rem;
    }
    .post-author { font-weight: 700; font-size: 1.02rem; }
    .post-date { color: rgba(255,255,255,0.45); font-size: 0.85rem; }
    .post-caption { margin-top: 0.6rem; font-size: 0.95rem; color: rgba(255,255,255,0.85); }

    .login-wrapper { max-width: 420px; margin: 2rem auto 0 auto; }
    .login-title { text-align: center; margin-bottom: 0.2rem; }
    .login-subtitle { text-align: center; color: rgba(255,255,255,0.5); margin-bottom: 1.8rem; }

    .sidebar-greeting { font-size: 1.1rem; font-weight: 700; margin-bottom: 0.2rem; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None
if 'upload_counter' not in st.session_state:
    st.session_state.upload_counter = 0


def get_headers():
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


# ---------------------------------------------------------------------------
# Login / Sign up page
# ---------------------------------------------------------------------------
def login_page():
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    st.markdown('<h1 class="login-title">🚀 Simple Social</h1>', unsafe_allow_html=True)
    st.markdown('<p class="login-subtitle">Share moments with people who matter</p>', unsafe_allow_html=True)

    email = st.text_input("Email", placeholder="you@example.com")
    password = st.text_input("Password", type="password", placeholder="••••••••")

    if email and password:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Login", type="primary", use_container_width=True):
                login_data = {"username": email, "password": password}
                with st.spinner("Logging in..."):
                    response = requests.post("http://localhost:8000/auth/jwt/login", data=login_data)

                if response.status_code == 200:
                    token_data = response.json()
                    st.session_state.token = token_data["access_token"]

                    user_response = requests.get("http://localhost:8000/auth/me", headers=get_headers())
                    if user_response.status_code == 200:
                        st.session_state.user = user_response.json()
                        st.rerun()
                    else:
                        st.error("Failed to get user info")
                else:
                    st.error("Invalid email or password!")

        with col2:
            if st.button("Sign Up", type="secondary", use_container_width=True):
                signup_data = {"email": email, "password": password}
                with st.spinner("Creating account..."):
                    response = requests.post("http://localhost:8000/auth/register", json=signup_data)

                if response.status_code == 201:
                    st.success("Account created! Click Login now.")
                else:
                    error_detail = response.json().get("detail", "Registration failed")
                    st.error(f"Registration failed: {error_detail}")
    else:
        st.info("Enter your email and password above to continue")

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Upload page
# ---------------------------------------------------------------------------
def upload_page():
    st.title("📸 Share Something")
    st.caption("Post a photo or video for your feed")

    uploaded_file = st.file_uploader(
        "Choose media",
        type=['png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'mkv', 'webm'],
        key=f"uploader_{st.session_state.upload_counter}"
    )
    caption = st.text_area(
        "Caption",
        placeholder="What's on your mind?",
        key=f"caption_{st.session_state.upload_counter}",
        height=100
    )

    st.write("")

    if uploaded_file and st.button("Share", type="primary"):
        with st.spinner("Uploading..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            data = {"caption": caption}
            response = requests.post("http://localhost:8000/upload", files=files, data=data, headers=get_headers())

        if response.status_code == 200:
            st.toast("Uploaded successfully! 🎉", icon="✅")
            st.session_state.upload_counter += 1
            st.rerun()
        else:
            st.error("Upload failed!")
    elif not uploaded_file:
        st.info("Pick an image or video above to get started")

def encode_text_for_overlay(text):
    if not text:
        return ""
    base64_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
    return urllib.parse.quote(base64_text)


def create_transformed_url(original_url, transformation_params, caption=None):
    if caption:
        encoded_caption = encode_text_for_overlay(caption)
        text_overlay = f"l-text,ie-{encoded_caption},ly-N20,lx-20,fs-100,co-white,bg-000000A0,l-end"
        transformation_params = text_overlay

    if not transformation_params:
        return original_url

    parts = original_url.split("/")
    file_path = "/".join(parts[4:])
    base_url = "/".join(parts[:4])
    return f"{base_url}/tr:{transformation_params}/{file_path}"

def feed_page():
    st.title("🏠 Feed")

    response = requests.get("http://localhost:8000/feed", headers=get_headers())
    if response.status_code == 200:
        posts = response.json()["posts"]

        if not posts:
            st.info("No posts yet! Be the first to share something.")
            return

        st.caption(f"{len(posts)} post{'s' if len(posts) != 1 else ''}")

        for post in posts:
            st.markdown('<div class="post-card">', unsafe_allow_html=True)

            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(
                    f'<div class="post-header">'
                    f'<span class="post-author">{post["email"]}</span>'
                    f'<span class="post-date">{post["created_at"][:10]}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with col2:
                if post.get('is_owner', False):
                    if st.button("🗑️", key=f"delete_{post['id']}", help="Delete post"):
                        del_response = requests.delete(
                            f"http://localhost:8000/posts/{post['id']}", headers=get_headers()
                        )
                        if del_response.status_code == 200:
                            st.toast("Post deleted", icon="🗑️")
                            st.rerun()
                        else:
                            st.error("Failed to delete post!")

            caption = post.get('caption', '')
            if post['file_type'] == 'image':
                uniform_url = create_transformed_url(post['url'], "", caption)
                st.image(uniform_url, width=320)
            else:
                uniform_video_url = create_transformed_url(
                    post['url'], "w-400,h-200,cm-pad_resize,bg-blurred"
                )
                st.video(uniform_video_url, width=320)
                if caption:
                    st.markdown(f'<div class="post-caption">{caption}</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("Failed to load feed")


if st.session_state.user is None:
    login_page()
else:
    st.sidebar.markdown(
        f'<div class="sidebar-greeting">👋 Hi, {st.session_state.user["email"].split("@")[0]}!</div>',
        unsafe_allow_html=True
    )
    st.sidebar.caption(st.session_state.user["email"])

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.user = None
        st.session_state.token = None
        st.rerun()

    st.sidebar.markdown("---")
    page = st.sidebar.radio("Navigate", ["🏠 Feed", "📸 Upload"], label_visibility="collapsed")

    if page == "🏠 Feed":
        feed_page()
    else:
        upload_page()