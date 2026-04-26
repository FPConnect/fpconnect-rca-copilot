from __future__ import annotations

import json
import mimetypes
import os
import secrets
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from .config import settings


class CloudDriveError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProviderConfig:
    key: str
    label: str
    auth_url: str
    token_url: str
    scopes: tuple[str, ...]
    client_id_env: str
    client_secret_env: str


_GOOGLE_FOLDER_MIME = "application/vnd.google-apps.folder"
_STATE_TTL_SECONDS = 15 * 60
_ONEDRIVE_SMALL_UPLOAD_LIMIT = 4 * 1024 * 1024

_PROVIDERS: dict[str, ProviderConfig] = {
    "google": ProviderConfig(
        key="google",
        label="Google Drive",
        auth_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        scopes=("https://www.googleapis.com/auth/drive",),
        client_id_env="GOOGLE_DRIVE_CLIENT_ID",
        client_secret_env="GOOGLE_DRIVE_CLIENT_SECRET",
    ),
    "onedrive": ProviderConfig(
        key="onedrive",
        label="OneDrive",
        auth_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
        scopes=("Files.ReadWrite", "offline_access", "User.Read"),
        client_id_env="ONEDRIVE_CLIENT_ID",
        client_secret_env="ONEDRIVE_CLIENT_SECRET",
    ),
}


def _cloud_store_path() -> Path:
    return settings.memory_path.parent / "cloud_drives.json"


def _default_public_base_url() -> str:
    explicit = os.getenv("AGENTE_AUTONOMO_PUBLIC_BASE_URL", "").strip()
    if explicit:
        return explicit.rstrip("/")
    host = os.getenv("AGENTE_AUTONOMO_HOST", "").strip() or os.getenv("HOST", "").strip() or "127.0.0.1"
    port = os.getenv("PORT", "").strip() or "8012"
    if host in {"0.0.0.0", "::"}:
        host = "127.0.0.1"
    return f"http://{host}:{port}".rstrip("/")


def _load_store() -> dict[str, Any]:
    path = _cloud_store_path()
    if not path.exists():
        return {"tokens": {}, "states": {}}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"tokens": {}, "states": {}}
    if not isinstance(payload, dict):
        return {"tokens": {}, "states": {}}
    payload.setdefault("tokens", {})
    payload.setdefault("states", {})
    return payload


def _save_store(store: dict[str, Any]) -> None:
    path = _cloud_store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(".tmp")
    temp_path.write_text(json.dumps(store, ensure_ascii=True, indent=2), encoding="utf-8")
    temp_path.replace(path)


def _cleanup_states(store: dict[str, Any]) -> None:
    now = int(time.time())
    states = store.get("states") or {}
    fresh_states = {
        key: value
        for key, value in states.items()
        if isinstance(value, dict) and now - int(value.get("created_at", 0) or 0) < _STATE_TTL_SECONDS
    }
    store["states"] = fresh_states


def _provider_key(raw: str) -> str:
    lowered = (raw or "").strip().lower()
    aliases = {
        "google": "google",
        "googledrive": "google",
        "google-drive": "google",
        "google_drive": "google",
        "drive": "google",
        "onedrive": "onedrive",
        "one-drive": "onedrive",
        "one_drive": "onedrive",
        "microsoft": "onedrive",
    }
    resolved = aliases.get(lowered, lowered)
    if resolved not in _PROVIDERS:
        raise CloudDriveError("Provedor invalido. Use 'google' ou 'onedrive'.")
    return resolved


def _provider_config(provider: str) -> ProviderConfig:
    return _PROVIDERS[_provider_key(provider)]


def _redirect_uri(provider: str, base_url: str | None = None) -> str:
    root = (base_url or _default_public_base_url()).rstrip("/")
    return f"{root}/api/cloud/oauth/{_provider_key(provider)}/callback"


def _provider_credentials(provider: str) -> tuple[str, str]:
    cfg = _provider_config(provider)
    client_id = os.getenv(cfg.client_id_env, "").strip()
    client_secret = os.getenv(cfg.client_secret_env, "").strip()
    if not client_id or not client_secret:
        raise CloudDriveError(
            f"Credenciais ausentes para {cfg.label}. Defina {cfg.client_id_env} e {cfg.client_secret_env}."
        )
    return client_id, client_secret


def _http_request(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: bytes | None = None,
    timeout: float = 30.0,
) -> tuple[int, bytes, dict[str, str]]:
    request = Request(url, data=body, method=method)
    for key, value in (headers or {}).items():
        request.add_header(key, value)
    try:
        with urlopen(request, timeout=timeout) as response:
            return int(response.status), response.read(), dict(response.headers.items())
    except HTTPError as exc:
        return int(exc.code), exc.read(), dict(exc.headers.items())
    except URLError as exc:
        raise CloudDriveError(f"Falha de rede ao falar com o provedor: {exc}") from exc


def _json_request(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: bytes | None = None,
    timeout: float = 30.0,
    expected: tuple[int, ...] = (200,),
) -> dict[str, Any]:
    status, payload, _ = _http_request(url, method=method, headers=headers, body=body, timeout=timeout)
    if status not in expected:
        try:
            parsed = json.loads(payload.decode("utf-8", errors="ignore"))
        except Exception:
            parsed = payload.decode("utf-8", errors="ignore")
        raise CloudDriveError(f"Falha HTTP {status}: {parsed}")
    if not payload:
        return {}
    try:
        return json.loads(payload.decode("utf-8", errors="ignore"))
    except Exception as exc:
        raise CloudDriveError("Resposta JSON invalida do provedor.") from exc


def _bytes_request(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: bytes | None = None,
    timeout: float = 30.0,
    expected: tuple[int, ...] = (200,),
) -> bytes:
    status, payload, _ = _http_request(url, method=method, headers=headers, body=body, timeout=timeout)
    if status not in expected:
        text = payload.decode("utf-8", errors="ignore")
        raise CloudDriveError(f"Falha HTTP {status}: {text}")
    return payload


def _authorized_headers(provider: str, access_token: str, *, json_content: bool = False) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {access_token}"}
    if json_content:
        headers["Content-Type"] = "application/json"
    return headers


def _scopes_string(provider: str) -> str:
    return " ".join(_provider_config(provider).scopes)


def _store_token(provider: str, payload: dict[str, Any]) -> dict[str, Any]:
    provider = _provider_key(provider)
    store = _load_store()
    token_store = store.setdefault("tokens", {})
    current = token_store.get(provider, {}) if isinstance(token_store.get(provider), dict) else {}
    expires_in = int(payload.get("expires_in", 3600) or 3600)
    refresh_token = payload.get("refresh_token") or current.get("refresh_token")
    token_store[provider] = {
        "access_token": payload.get("access_token", ""),
        "refresh_token": refresh_token or "",
        "expires_at": int(time.time()) + max(60, expires_in - 30),
        "scope": payload.get("scope", current.get("scope", _scopes_string(provider))),
        "token_type": payload.get("token_type", current.get("token_type", "Bearer")),
        "account_label": current.get("account_label", ""),
        "account_email": current.get("account_email", ""),
        "drive_id": current.get("drive_id", ""),
        "updated_at": int(time.time()),
    }
    _save_store(store)
    return token_store[provider]


def _update_token_metadata(provider: str, **fields: str) -> None:
    provider = _provider_key(provider)
    store = _load_store()
    token_store = store.setdefault("tokens", {})
    current = token_store.get(provider)
    if not isinstance(current, dict):
        return
    for key, value in fields.items():
        if value:
            current[key] = value
    token_store[provider] = current
    _save_store(store)


def _refresh_access_token(provider: str) -> dict[str, Any]:
    provider = _provider_key(provider)
    cfg = _provider_config(provider)
    client_id, client_secret = _provider_credentials(provider)
    store = _load_store()
    token_store = store.get("tokens", {})
    current = token_store.get(provider)
    if not isinstance(current, dict) or not current.get("refresh_token"):
        raise CloudDriveError(f"Nao ha refresh token salvo para {cfg.label}. Conecte a conta novamente.")
    body = urlencode(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": current["refresh_token"],
            "scope": _scopes_string(provider),
        }
    ).encode("utf-8")
    payload = _json_request(
        cfg.token_url,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body=body,
    )
    return _store_token(provider, payload)


def _access_token(provider: str) -> str:
    provider = _provider_key(provider)
    store = _load_store()
    token_store = store.get("tokens", {})
    current = token_store.get(provider)
    if not isinstance(current, dict) or not current.get("access_token"):
        raise CloudDriveError(f"{_provider_config(provider).label} ainda nao esta conectado.")
    if int(current.get("expires_at", 0) or 0) <= int(time.time()) + 30:
        current = _refresh_access_token(provider)
    return str(current.get("access_token") or "")


def _google_escape_query(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def _normalize_path(path: str) -> str:
    cleaned = (path or "/").strip()
    if not cleaned:
        return "/"
    if not cleaned.startswith("/"):
        cleaned = "/" + cleaned
    while "//" in cleaned:
        cleaned = cleaned.replace("//", "/")
    if len(cleaned) > 1 and cleaned.endswith("/"):
        cleaned = cleaned[:-1]
    return cleaned or "/"


def _split_parent(path: str) -> tuple[str, str]:
    normalized = _normalize_path(path)
    if normalized == "/":
        raise CloudDriveError("Informe um caminho abaixo da raiz.")
    parent, _, name = normalized.rpartition("/")
    return (parent or "/"), name


def _google_list_children(parent_id: str, *, name: str | None = None) -> list[dict[str, Any]]:
    token = _access_token("google")
    filters = [f"'{parent_id}' in parents", "trashed = false"]
    if name:
        filters.append(f"name = '{_google_escape_query(name)}'")
    query = " and ".join(filters)
    params = urlencode(
        {
            "q": query,
            "fields": "files(id,name,mimeType,parents,size,modifiedTime,webViewLink)",
            "pageSize": "200",
            "supportsAllDrives": "true",
            "includeItemsFromAllDrives": "true",
        }
    )
    payload = _json_request(
        f"https://www.googleapis.com/drive/v3/files?{params}",
        headers=_authorized_headers("google", token),
    )
    items = payload.get("files", [])
    return items if isinstance(items, list) else []


def _google_get_item(file_id: str) -> dict[str, Any]:
    token = _access_token("google")
    params = urlencode({"fields": "id,name,mimeType,parents,size,modifiedTime,webViewLink"})
    return _json_request(
        f"https://www.googleapis.com/drive/v3/files/{file_id}?{params}",
        headers=_authorized_headers("google", token),
    )


def _google_resolve_path(path: str) -> dict[str, Any] | None:
    normalized = _normalize_path(path)
    if normalized == "/":
        return {"id": "root", "name": "/", "mimeType": _GOOGLE_FOLDER_MIME}
    current_id = "root"
    current_item: dict[str, Any] | None = None
    for segment in normalized.strip("/").split("/"):
        matches = _google_list_children(current_id, name=segment)
        if not matches:
            return None
        current_item = matches[0]
        current_id = str(current_item.get("id") or "")
        if not current_id:
            return None
    return current_item


def _google_ensure_folder(path: str) -> dict[str, Any]:
    normalized = _normalize_path(path)
    if normalized == "/":
        return {"id": "root", "name": "/", "mimeType": _GOOGLE_FOLDER_MIME}
    current_id = "root"
    current_item: dict[str, Any] = {"id": "root", "name": "/", "mimeType": _GOOGLE_FOLDER_MIME}
    token = _access_token("google")
    for segment in normalized.strip("/").split("/"):
        matches = [item for item in _google_list_children(current_id, name=segment) if item.get("mimeType") == _GOOGLE_FOLDER_MIME]
        if matches:
            current_item = matches[0]
            current_id = str(current_item.get("id") or "")
            continue
        metadata = {"name": segment, "mimeType": _GOOGLE_FOLDER_MIME, "parents": [current_id]}
        payload = _json_request(
            "https://www.googleapis.com/drive/v3/files?fields=id,name,mimeType,parents,webViewLink",
            method="POST",
            headers=_authorized_headers("google", token, json_content=True),
            body=json.dumps(metadata).encode("utf-8"),
        )
        current_item = payload
        current_id = str(payload.get("id") or "")
    return current_item


def _google_multipart_body(metadata: dict[str, Any], content: bytes, mime_type: str) -> tuple[bytes, str]:
    boundary = f"agente-autonomo-{secrets.token_hex(12)}"
    parts = [
        f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n".encode("utf-8"),
        json.dumps(metadata).encode("utf-8"),
        f"\r\n--{boundary}\r\nContent-Type: {mime_type}\r\n\r\n".encode("utf-8"),
        content,
        f"\r\n--{boundary}--\r\n".encode("utf-8"),
    ]
    return b"".join(parts), boundary


def _google_write_bytes(remote_path: str, content: bytes, mime_type: str) -> dict[str, Any]:
    parent_path, file_name = _split_parent(remote_path)
    parent = _google_ensure_folder(parent_path)
    token = _access_token("google")
    existing_matches = [
        item
        for item in _google_list_children(str(parent.get("id") or "root"), name=file_name)
        if item.get("mimeType") != _GOOGLE_FOLDER_MIME
    ]
    metadata = {"name": file_name, "parents": [str(parent.get("id") or "root")], "mimeType": mime_type}
    body, boundary = _google_multipart_body(metadata, content, mime_type)
    headers = _authorized_headers("google", token)
    headers["Content-Type"] = f"multipart/related; boundary={boundary}"
    if existing_matches:
        file_id = str(existing_matches[0].get("id") or "")
        return _json_request(
            f"https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=multipart&fields=id,name,mimeType,webViewLink,modifiedTime",
            method="PATCH",
            headers=headers,
            body=body,
        )
    return _json_request(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,mimeType,webViewLink,modifiedTime",
        method="POST",
        headers=headers,
        body=body,
    )


def _google_fetch_account_metadata() -> None:
    token = _access_token("google")
    payload = _json_request(
        "https://www.googleapis.com/drive/v3/about?fields=user(displayName,emailAddress)",
        headers=_authorized_headers("google", token),
    )
    user = payload.get("user") or {}
    if isinstance(user, dict):
        _update_token_metadata(
            "google",
            account_label=str(user.get("displayName") or user.get("emailAddress") or ""),
            account_email=str(user.get("emailAddress") or ""),
        )


def _onedrive_path_url(path: str, suffix: str = "") -> str:
    normalized = _normalize_path(path)
    if normalized == "/":
        return f"https://graph.microsoft.com/v1.0/me/drive/root{suffix}"
    encoded_path = "/".join(quote(part, safe="") for part in normalized.strip("/").split("/"))
    return f"https://graph.microsoft.com/v1.0/me/drive/root:/{encoded_path}:{suffix}"


def _onedrive_item(path: str) -> dict[str, Any]:
    token = _access_token("onedrive")
    return _json_request(
        _onedrive_path_url(path, "?$select=id,name,size,webUrl,parentReference,file,folder,lastModifiedDateTime"),
        headers=_authorized_headers("onedrive", token),
    )


def _onedrive_folder_children(path: str) -> list[dict[str, Any]]:
    token = _access_token("onedrive")
    payload = _json_request(
        _onedrive_path_url(path, "/children?$select=id,name,size,webUrl,file,folder,lastModifiedDateTime,parentReference"),
        headers=_authorized_headers("onedrive", token),
    )
    values = payload.get("value", [])
    return values if isinstance(values, list) else []


def _onedrive_ensure_folder(path: str) -> dict[str, Any]:
    normalized = _normalize_path(path)
    if normalized == "/":
        return _onedrive_item("/")
    token = _access_token("onedrive")
    current_path = "/"
    current_item = _onedrive_item("/")
    for segment in normalized.strip("/").split("/"):
        next_path = current_path.rstrip("/") + "/" + segment if current_path != "/" else "/" + segment
        try:
            current_item = _onedrive_item(next_path)
            if "folder" not in current_item:
                raise CloudDriveError(f"O caminho {next_path} existe, mas nao e uma pasta.")
            current_path = next_path
            continue
        except CloudDriveError as exc:
            if "Falha HTTP 404" not in str(exc):
                raise
        create_url = _onedrive_path_url(current_path, "/children")
        payload = _json_request(
            create_url,
            method="POST",
            headers=_authorized_headers("onedrive", token, json_content=True),
            body=json.dumps(
                {
                    "name": segment,
                    "folder": {},
                    "@microsoft.graph.conflictBehavior": "fail",
                }
            ).encode("utf-8"),
            expected=(200, 201),
        )
        current_item = payload
        current_path = next_path
    return current_item


def _onedrive_upload_bytes(remote_path: str, content: bytes, mime_type: str) -> dict[str, Any]:
    parent_path, _ = _split_parent(remote_path)
    _onedrive_ensure_folder(parent_path)
    token = _access_token("onedrive")
    if len(content) <= _ONEDRIVE_SMALL_UPLOAD_LIMIT:
        return _json_request(
            _onedrive_path_url(remote_path, "/content"),
            method="PUT",
            headers={"Authorization": f"Bearer {token}", "Content-Type": mime_type},
            body=content,
            expected=(200, 201),
        )

    session_payload = _json_request(
        _onedrive_path_url(remote_path, "/createUploadSession"),
        method="POST",
        headers=_authorized_headers("onedrive", token, json_content=True),
        body=json.dumps({"item": {"@microsoft.graph.conflictBehavior": "replace"}}).encode("utf-8"),
        expected=(200,),
    )
    upload_url = str(session_payload.get("uploadUrl") or "")
    if not upload_url:
        raise CloudDriveError("O provedor nao retornou uploadUrl para upload grande no OneDrive.")
    total = len(content)
    headers = {
        "Content-Length": str(total),
        "Content-Range": f"bytes 0-{total - 1}/{total}",
        "Content-Type": "application/octet-stream",
    }
    return _json_request(upload_url, method="PUT", headers=headers, body=content, expected=(200, 201, 202))


def _onedrive_fetch_account_metadata() -> None:
    token = _access_token("onedrive")
    me = _json_request(
        "https://graph.microsoft.com/v1.0/me?$select=displayName,userPrincipalName",
        headers=_authorized_headers("onedrive", token),
    )
    _update_token_metadata(
        "onedrive",
        account_label=str(me.get("displayName") or me.get("userPrincipalName") or ""),
        account_email=str(me.get("userPrincipalName") or ""),
    )


def list_cloud_provider_statuses() -> list[dict[str, Any]]:
    store = _load_store()
    statuses: list[dict[str, Any]] = []
    for provider, cfg in _PROVIDERS.items():
        token = store.get("tokens", {}).get(provider, {})
        configured = bool(os.getenv(cfg.client_id_env, "").strip() and os.getenv(cfg.client_secret_env, "").strip())
        statuses.append(
            {
                "provider": provider,
                "label": cfg.label,
                "configured": configured,
                "connected": bool(isinstance(token, dict) and token.get("access_token")),
                "account_label": str(token.get("account_label") or "") if isinstance(token, dict) else "",
                "account_email": str(token.get("account_email") or "") if isinstance(token, dict) else "",
                "expires_at": int(token.get("expires_at", 0) or 0) if isinstance(token, dict) else 0,
                "redirect_uri": _redirect_uri(provider),
            }
        )
    return statuses


def cloud_drive_status_summary() -> str:
    lines = ["Estado das conexoes de armazenamento em nuvem:"]
    for item in list_cloud_provider_statuses():
        state = "conectado" if item["connected"] else "desconectado"
        suffix = f" ({item['account_label']})" if item.get("account_label") else ""
        lines.append(f"- {item['label']}: {state}{suffix}")
    lines.append("Use 'drive connect google' ou 'drive connect onedrive' para iniciar a conexao.")
    return "\n".join(lines)


def start_cloud_oauth(provider: str, base_url: str | None = None) -> str:
    provider = _provider_key(provider)
    cfg = _provider_config(provider)
    client_id, _ = _provider_credentials(provider)
    redirect_uri = _redirect_uri(provider, base_url=base_url)
    store = _load_store()
    _cleanup_states(store)
    state = secrets.token_urlsafe(24)
    store.setdefault("states", {})[state] = {
        "provider": provider,
        "redirect_uri": redirect_uri,
        "created_at": int(time.time()),
    }
    _save_store(store)

    params: dict[str, str] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": _scopes_string(provider),
        "state": state,
    }
    if provider == "google":
        params["access_type"] = "offline"
        params["include_granted_scopes"] = "true"
        params["prompt"] = "consent"
    else:
        params["response_mode"] = "query"
        params["prompt"] = "select_account"
    return f"{cfg.auth_url}?{urlencode(params)}"


def connect_cloud_provider(provider: str, base_url: str | None = None) -> str:
    url = start_cloud_oauth(provider, base_url=base_url)
    try:
        webbrowser.open(url)
        opened = "Abri a autorizacao no navegador padrao."
    except Exception:
        opened = "Nao consegui abrir o navegador automaticamente."
    return (
        f"{opened} Conclua a conexao de {_provider_config(provider).label} em: {url}\n"
        f"O callback esperado e {_redirect_uri(provider, base_url=base_url)}."
    )


def complete_cloud_oauth(provider: str, code: str, state: str) -> dict[str, Any]:
    provider = _provider_key(provider)
    cfg = _provider_config(provider)
    client_id, client_secret = _provider_credentials(provider)
    store = _load_store()
    _cleanup_states(store)
    state_payload = store.get("states", {}).pop(state, None)
    _save_store(store)
    if not isinstance(state_payload, dict) or state_payload.get("provider") != provider:
        raise CloudDriveError("Estado OAuth invalido ou expirado.")
    redirect_uri = str(state_payload.get("redirect_uri") or _redirect_uri(provider))
    body = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    if provider == "onedrive":
        body["scope"] = _scopes_string(provider)
    payload = _json_request(
        cfg.token_url,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body=urlencode(body).encode("utf-8"),
    )
    _store_token(provider, payload)
    if provider == "google":
        _google_fetch_account_metadata()
    else:
        _onedrive_fetch_account_metadata()
    statuses = {item["provider"]: item for item in list_cloud_provider_statuses()}
    return statuses[provider]


def disconnect_cloud_provider(provider: str) -> str:
    provider = _provider_key(provider)
    store = _load_store()
    tokens = store.setdefault("tokens", {})
    tokens.pop(provider, None)
    _save_store(store)
    return f"Conexao com {_provider_config(provider).label} removida."


def cloud_drive_list(provider: str, path: str = "/") -> str:
    provider = _provider_key(provider)
    normalized = _normalize_path(path)
    if provider == "google":
        item = _google_resolve_path(normalized)
        if item is None:
            raise CloudDriveError(f"Caminho nao encontrado em Google Drive: {normalized}")
        if item.get("mimeType") != _GOOGLE_FOLDER_MIME:
            url = str(item.get("webViewLink") or "")
            return f"Arquivo encontrado em {normalized}: {item.get('name')} ({url})"
        children = _google_list_children(str(item.get("id") or "root"))
        if not children:
            return f"A pasta {normalized} esta vazia no Google Drive."
        lines = [f"Itens em Google Drive {normalized}:"]
        for child in children[:50]:
            kind = "pasta" if child.get("mimeType") == _GOOGLE_FOLDER_MIME else "arquivo"
            lines.append(f"- {child.get('name')} [{kind}]")
        return "\n".join(lines)

    item = _onedrive_item(normalized)
    if "folder" not in item:
        url = str(item.get("webUrl") or "")
        return f"Arquivo encontrado em {normalized}: {item.get('name')} ({url})"
    children = _onedrive_folder_children(normalized)
    if not children:
        return f"A pasta {normalized} esta vazia no OneDrive."
    lines = [f"Itens em OneDrive {normalized}:"]
    for child in children[:50]:
        kind = "pasta" if "folder" in child else "arquivo"
        lines.append(f"- {child.get('name')} [{kind}]")
    return "\n".join(lines)


def cloud_drive_make_directory(provider: str, path: str) -> str:
    provider = _provider_key(provider)
    normalized = _normalize_path(path)
    if provider == "google":
        folder = _google_ensure_folder(normalized)
        return f"Pasta pronta no Google Drive: {normalized} (id {folder.get('id')})"
    folder = _onedrive_ensure_folder(normalized)
    return f"Pasta pronta no OneDrive: {normalized} (id {folder.get('id')})"


def cloud_drive_read_text(provider: str, path: str, limit: int = 4000) -> str:
    provider = _provider_key(provider)
    normalized = _normalize_path(path)
    if provider == "google":
        item = _google_resolve_path(normalized)
        if item is None:
            raise CloudDriveError(f"Caminho nao encontrado em Google Drive: {normalized}")
        if item.get("mimeType") == _GOOGLE_FOLDER_MIME:
            raise CloudDriveError("O caminho informado e uma pasta. Informe um arquivo.")
        token = _access_token("google")
        mime_type = str(item.get("mimeType") or "")
        if mime_type.startswith("application/vnd.google-apps"):
            content = _bytes_request(
                f"https://www.googleapis.com/drive/v3/files/{item['id']}/export?mimeType=text/plain",
                headers=_authorized_headers("google", token),
            )
        else:
            content = _bytes_request(
                f"https://www.googleapis.com/drive/v3/files/{item['id']}?alt=media",
                headers=_authorized_headers("google", token),
            )
        return f"Conteudo de {normalized}:\n{content.decode('utf-8', errors='ignore')[:limit]}"

    item = _onedrive_item(normalized)
    if "folder" in item:
        raise CloudDriveError("O caminho informado e uma pasta. Informe um arquivo.")
    token = _access_token("onedrive")
    content = _bytes_request(
        _onedrive_path_url(normalized, "/content"),
        headers={"Authorization": f"Bearer {token}"},
    )
    return f"Conteudo de {normalized}:\n{content.decode('utf-8', errors='ignore')[:limit]}"


def cloud_drive_write_text(provider: str, path: str, content: str) -> str:
    provider = _provider_key(provider)
    normalized = _normalize_path(path)
    raw = content.encode("utf-8")
    if provider == "google":
        item = _google_write_bytes(normalized, raw, "text/plain; charset=utf-8")
        return f"Arquivo atualizado no Google Drive: {normalized} ({item.get('webViewLink') or item.get('id')})"
    item = _onedrive_upload_bytes(normalized, raw, "text/plain; charset=utf-8")
    return f"Arquivo atualizado no OneDrive: {normalized} ({item.get('webUrl') or item.get('id')})"


def cloud_drive_upload_local_file(provider: str, local_path: str, remote_path: str) -> str:
    provider = _provider_key(provider)
    source = Path(local_path).expanduser()
    if not source.exists() or not source.is_file():
        raise CloudDriveError(f"Arquivo local nao encontrado: {source}")
    content = source.read_bytes()
    mime_type = mimetypes.guess_type(source.name)[0] or "application/octet-stream"
    normalized = _normalize_path(remote_path)
    if provider == "google":
        item = _google_write_bytes(normalized, content, mime_type)
        return f"Upload concluido para Google Drive: {normalized} ({item.get('webViewLink') or item.get('id')})"
    item = _onedrive_upload_bytes(normalized, content, mime_type)
    return f"Upload concluido para OneDrive: {normalized} ({item.get('webUrl') or item.get('id')})"


def cloud_drive_rename(provider: str, path: str, new_name: str) -> str:
    provider = _provider_key(provider)
    normalized = _normalize_path(path)
    clean_name = new_name.strip().strip("/")
    if not clean_name:
        raise CloudDriveError("Novo nome vazio.")
    if provider == "google":
        item = _google_resolve_path(normalized)
        if item is None:
            raise CloudDriveError(f"Caminho nao encontrado em Google Drive: {normalized}")
        token = _access_token("google")
        payload = _json_request(
            f"https://www.googleapis.com/drive/v3/files/{item['id']}?fields=id,name,webViewLink",
            method="PATCH",
            headers=_authorized_headers("google", token, json_content=True),
            body=json.dumps({"name": clean_name}).encode("utf-8"),
        )
        return f"Item renomeado no Google Drive para {payload.get('name')}."
    item = _onedrive_item(normalized)
    token = _access_token("onedrive")
    payload = _json_request(
        f"https://graph.microsoft.com/v1.0/me/drive/items/{item['id']}",
        method="PATCH",
        headers=_authorized_headers("onedrive", token, json_content=True),
        body=json.dumps({"name": clean_name}).encode("utf-8"),
    )
    return f"Item renomeado no OneDrive para {payload.get('name')}."


def cloud_drive_move(provider: str, path: str, destination_folder: str) -> str:
    provider = _provider_key(provider)
    normalized = _normalize_path(path)
    destination = _normalize_path(destination_folder)
    if provider == "google":
        item = _google_resolve_path(normalized)
        if item is None:
            raise CloudDriveError(f"Caminho nao encontrado em Google Drive: {normalized}")
        dest = _google_ensure_folder(destination)
        token = _access_token("google")
        current_parents = ",".join(item.get("parents") or [])
        params = urlencode(
            {
                "addParents": str(dest.get("id") or ""),
                "removeParents": current_parents,
                "fields": "id,name,parents,webViewLink",
            }
        )
        payload = _json_request(
            f"https://www.googleapis.com/drive/v3/files/{item['id']}?{params}",
            method="PATCH",
            headers=_authorized_headers("google", token),
        )
        return f"Item movido no Google Drive para {destination} ({payload.get('name')})."

    item = _onedrive_item(normalized)
    dest = _onedrive_ensure_folder(destination)
    token = _access_token("onedrive")
    payload = _json_request(
        f"https://graph.microsoft.com/v1.0/me/drive/items/{item['id']}",
        method="PATCH",
        headers=_authorized_headers("onedrive", token, json_content=True),
        body=json.dumps({"parentReference": {"id": dest.get("id")}}).encode("utf-8"),
    )
    return f"Item movido no OneDrive para {destination} ({payload.get('name')})."


def cloud_drive_delete(provider: str, path: str) -> str:
    provider = _provider_key(provider)
    normalized = _normalize_path(path)
    if provider == "google":
        item = _google_resolve_path(normalized)
        if item is None:
            raise CloudDriveError(f"Caminho nao encontrado em Google Drive: {normalized}")
        token = _access_token("google")
        _json_request(
            f"https://www.googleapis.com/drive/v3/files/{item['id']}",
            method="DELETE",
            headers=_authorized_headers("google", token),
            expected=(204,),
        )
        return f"Item removido do Google Drive: {normalized}"

    item = _onedrive_item(normalized)
    token = _access_token("onedrive")
    _json_request(
        f"https://graph.microsoft.com/v1.0/me/drive/items/{item['id']}",
        method="DELETE",
        headers=_authorized_headers("onedrive", token),
        expected=(204,),
    )
    return f"Item removido do OneDrive: {normalized}"
