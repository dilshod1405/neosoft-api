import requests
from django.conf import settings
from requests_toolbelt import MultipartEncoder
import requests

API_BASE = settings.VDOCIPHER_API_BASE.rstrip("/")
API_KEY = settings.VDOCIPHER_API_KEY

HEADERS = {
    "Authorization": f"Apisecret {API_KEY}",
    "Accept": "application/json",
}




# ============================================================
#                  CREATE FOLDER ON VDOCIPHER
# ============================================================

def create_folder(name: str, parent_folder_id: str = None) -> dict:
    url = f"{API_BASE}/videos/folders"
    payload = {"name": name}
    if parent_folder_id:
        payload["parent"] = parent_folder_id
    resp = requests.post(
        url,
        headers={**HEADERS, "Content-Type": "application/json"},
        json=payload,
        timeout=30
    )
    resp.raise_for_status()
    return resp.json()




# ============================================================
#            INIATE VIDEO UPLOAD AND GET CREDENTIALS
# ============================================================

def obtain_upload_credentials(folder_id: str = None, title: str = None) -> dict:
    url = f"{API_BASE}/videos"
    params = {}
    if title:
        params["title"] = title
    if folder_id:
        params["folderId"] = folder_id
    resp = requests.put(url, headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()




# ====================================================
#               UPLOAD VIDEO TO AMAZON S3
# ====================================================

def upload_video(file, upload_url: str, title: str, credentials: dict) -> dict:
    client_payload = credentials.get("clientPayload", {})

    m = MultipartEncoder(fields=[
        ('x-amz-credential', client_payload['x-amz-credential']),
        ('x-amz-algorithm', client_payload['x-amz-algorithm']),
        ('x-amz-date', client_payload['x-amz-date']),
        ('x-amz-signature', client_payload['x-amz-signature']),
        ('key', client_payload['key']),
        ('policy', client_payload['policy']),
        ('success_action_status', '201'),
        ('success_action_redirect', ''),
        ('file', (getattr(file, "name", title), file, 'video/mp4')),
    ])

    response = requests.post(upload_url, data=m, headers={'Content-Type': m.content_type}, timeout=600)
    print("Upload Response:", response.status_code, response.text)

    response.raise_for_status()
    if response.status_code == 201:
        return {"status": "success"}
    else:
        return {"status": "error", "details": response.text}




# ======================================================
#               GET STATUS OF UPLOADED VIDEO
# ======================================================

def get_video_status(video_id: str) -> dict:
    url = f"{API_BASE}/videos/{video_id}"
    headers = HEADERS
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()




# ====================================================
#               GENERATE OTP FOR VIDEO
# ====================================================

def generate_otp(video_id: str, ttl: int = 300) -> dict:
    url = f"{API_BASE}/videos/{video_id}/otp"
    headers = HEADERS
    payload = {"ttl": int(ttl)}
    resp = requests.post(url, headers=headers, json=payload, timeout=15)
    resp.raise_for_status()
    return resp.json()




# ====================================================
#                GET UPLOADED VIDEOS
# ====================================================

def get_videos(page: int = 1, limit: int = 20, q: str = None, tags: str = None, folder_id: str = None):
    url = f"{API_BASE}/videos?page={page}&limit={limit}"

    params = {}
    if q:
        params["q"] = q
    if tags:
        params["tags"] = tags
    if folder_id:
        params["folderId"] = folder_id

    resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()




# ====================================================
#              RENAME UPLOADED VIDEO NAME
# ====================================================

def rename_video(video_id: str, new_title: str) -> dict:
    url = f"{API_BASE}/videos/{video_id}"
    headers = HEADERS
    payload = {"title": new_title}
    resp = requests.post(url, headers=headers, json=payload, timeout=15)
    resp.raise_for_status()
    return resp.json()
