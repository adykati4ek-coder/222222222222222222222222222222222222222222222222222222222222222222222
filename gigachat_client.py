import os
import time
import requests


class GigaChatClient:
    def __init__(self):
        self.client_id = os.getenv("GIGACHAT_CLIENT_ID", "").strip()
        self.client_secret = os.getenv("GIGACHAT_CLIENT_SECRET", "").strip()
        self.api_key = os.getenv("GIGACHAT_API_KEY", "").strip()
        self.auth_url = os.getenv("GIGACHAT_AUTH_URL", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth")
        self.api_url = os.getenv("GIGACHAT_API_URL", "https://gigachat.devices.sberbank.ru/api/v1/chat/completions")
        self._token = None
        self._token_expires = 0

    def _get_token(self):
        if time.time() < self._token_expires and self._token:
            return self._token
        if self.api_key:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "RqUID": "5f0846b7-1fb3-4c35-99a4-c7f9f9f9f9f9",
            }
            data = {"scope": "GIGACHAT_API_PERS"}
            payload = self.api_key
        else:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "Authorization": "Basic "
                + __import__("base64").b64encode(
                    f"{self.client_id}:{self.client_secret}".encode()
                ).decode(),
                "RqUID": "5f0846b7-1fb3-4c35-99a4-c7f9f9f9f9f9",
            }
            data = {"scope": "GIGACHAT_API_PERS"}
            payload = None
        resp = requests.post(self.auth_url, headers=headers, data=data, json=payload, timeout=30, verify=False)
        resp.raise_for_status()
        j = resp.json()
        self._token = j["access_token"]
        self._token_expires = time.time() + max(int(j.get("expires_at", 1800)) // 1000 - 60, 60)
        return self._token

    def chat(self, system, user_text, temperature=0.8):
        token = self._get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        body = {
            "model": "GigaChat-Pro",
            "temperature": temperature,
            "max_tokens": 4096,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user_text},
            ],
        }
        resp = requests.post(self.api_url, headers=headers, json=body, timeout=120, verify=False)
        resp.raise_for_status()
        j = resp.json()
        return j["choices"][0]["message"]["content"].strip()