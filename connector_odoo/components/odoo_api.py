# Copyright 2023 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import base64
import logging
from random import randint

import requests

from odoo.addons.connector.exception import IDMissingInBackend, RetryableJobError

_logger = logging.getLogger(__name__)


class OdooAPI:
    """
    Yet another Odoo API client with JSON-RPC.
    """

    def __init__(
        self,
        base_url,
        db,
        login,
        password,
        timeout=15,
        uid=0,
        default_lang="tr_TR",
        translation_langs=None,
    ):
        self.base_url = base_url
        self.db = db
        self.login = login
        self.password = password
        self.timeout = timeout
        self._default_lang = default_lang
        self._translation_langs = translation_langs
        self._session = requests.Session()
        self._uid = self._get_uid() if uid == 0 else uid
        if not self._uid:
            _logger.error("OdooAPI: Authentication failed. Username: %s", self.login)

    def __repr__(self):
        return f"<OdooAPI {self.base_url}>"

    @property
    def query_id(self):
        return randint(1, 99999)

    def _post(self, payload):
        try:
            response = self._session.post(
                self.base_url + "/jsonrpc",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            json_resp = response.json()
            if json_resp.get("error"):
                raise requests.HTTPError(json_resp["error"])
            return json_resp["result"] if ("result" in json_resp) else None
        except Exception as exc:
            _logger.error(exc)
            raise RetryableJobError(
                f"OdooAPI: Connection error: {exc}",
                seconds=5,
            )

    def _base_payload(self):
        return {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {},
            "id": self.query_id,
        }

    def _build_context(self, context=None):
        _ctx = {
            "lang": self._default_lang,
            "connector_request": True,
        }
        if context:
            _ctx.update(context)
        # Add translation languages to context
        if self._translation_langs:
            _ctx["translation_lang_codes"] = self._translation_langs
        return _ctx

    def _build_authenticate_payload(self):
        return [
            self.db,
            hasattr(self, "_uid") and self._uid or self.login,
            self.password,
        ]

    def _build_common_payload(self, method, kwargs=None, send_kwargs=True):
        payload = self._base_payload()
        args = self._build_authenticate_payload() + (kwargs or [])
        data = {
            "service": "common",
            "method": method,
            "args": [],
        }
        if send_kwargs:
            data["args"] = args

        payload["params"].update(data)
        return payload

    def _build_execute_kw_payload(
        self,
        kwargs=None,
    ):
        payload = self._base_payload()
        args = self._build_authenticate_payload() + (kwargs or [])
        data = {
            "service": "object",
            "method": "execute_kw",
            "args": args,
        }
        payload["params"].update(data)
        return payload

    def _get_uid(self):
        return self._post(
            self._build_common_payload(
                method="login",
            )
        )

    def _web_login(self):
        """
        Authenticate via web session endpoint to establish a session cookie.

        This is required for downloading attachments via /web/content/ URLs,
        as JSON-RPC authentication doesn't establish a web session.
        """
        url = f"{self.base_url}/web/session/authenticate"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": self.db,
                "login": self.login,
                "password": self.password,
            },
            "id": self.query_id,
        }
        try:
            response = self._session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            if result.get("error"):
                _logger.error("Web login failed: %s", result["error"])
                return False
            return result.get("result", {}).get("uid")
        except requests.exceptions.RequestException as exc:
            _logger.error("Web login request failed: %s", exc)
            return False

    def test_connection(self):
        response = self._post(
            self._build_common_payload(
                method="version",
                send_kwargs=False,
            )
        )
        _logger.info("OdooAPI Connection test successful, version: %s", response)
        return True

    def create(self, model, data, context=None):
        return self._post(
            self._build_execute_kw_payload(
                kwargs=[
                    model,
                    "create",
                    [data],
                    {
                        "context": self._build_context(context=context),
                    },
                ],
            )
        )

    def search(
        self,
        model,
        domain,
        offset=0,
        fields=None,
        limit=None,
        order=None,
        context=None,
        get_passive=None,
    ):
        if get_passive:
            base_domain = ["|", ["active", "=", True], ["active", "=", False]]
        else:
            base_domain = []
        base_domain.extend(domain)
        return self._post(
            self._build_execute_kw_payload(
                kwargs=[
                    model,
                    "search_read",
                    [base_domain],
                    {
                        "fields": fields,
                        "offset": offset,
                        "limit": limit,
                        "order": order,
                        "context": self._build_context(context=context),
                    },
                ],
            )
        )

    def write(self, res_id, model, data, context=None):
        """
        Single record writes.
        """
        return self._post(
            self._build_execute_kw_payload(
                kwargs=[
                    model,
                    "write",
                    [[res_id], data],
                    {
                        "context": self._build_context(context=context),
                    },
                ],
            )
        )

    def browse(self, model, res_id, fields=None, context=None, get_passive=None):
        if get_passive:
            base_domain = ["|", ["active", "=", True], ["active", "=", False]]
        else:
            base_domain = []

        if res := self._post(
            self._build_execute_kw_payload(
                kwargs=[
                    model,
                    "search_read",
                    [base_domain + [["id", "=", res_id]]],
                    {
                        "fields": fields,
                        "context": self._build_context(context=context),
                    },
                ],
            )
        ):
            return res[0]
        else:
            raise IDMissingInBackend(f"ID {res_id} not found in backend")

    def unlink(self, res_id):
        raise NotImplementedError

    def execute(self, model, method, args=None, context=None):
        return self._post(
            self._build_execute_kw_payload(
                kwargs=[
                    model,
                    method,
                    args or [],
                    {
                        "context": self._build_context(context=context),
                    },
                ],
            )
        )

    def download_attachment(self, download_path, timeout=300):
        """
        Download attachment binary data via HTTP streaming.

        Uses the attachment's download path to stream large files
        without JSON-RPC overhead.

        :param download_path: The download path for the attachment
                              (e.g., /web/content/ir.attachment/123/datas)
        :param timeout: Timeout in seconds for the download (default: 300)
        :return: base64 encoded binary data as string, or False if download fails
        """
        # Ensure we have a valid web session
        if not self._web_login():
            raise RetryableJobError(
                f"Download attachment {download_path} failed: web login failed",
                seconds=10,
            )

        url = f"{self.base_url}{download_path}"

        try:
            response = self._session.get(
                url,
                stream=True,
                timeout=timeout,
            )
            response.raise_for_status()

            # Check if redirected to login page (session expired)
            if "text/html" in response.headers.get("Content-Type", ""):
                _logger.warning(
                    "Download attachment %s: session expired, re-authenticating",
                    download_path,
                )
                if not self._web_login():
                    raise RetryableJobError(
                        f"Download attachment {download_path} failed: "
                        "re-authentication failed",
                        seconds=10,
                    )
                response = self._session.get(
                    url,
                    stream=True,
                    timeout=timeout,
                )
                response.raise_for_status()

            # Stream content in chunks
            chunks = []
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    chunks.append(chunk)

            binary_data = b"".join(chunks)
            return base64.b64encode(binary_data).decode("ascii")

        except requests.exceptions.RequestException as exc:
            _logger.error("Download attachment %s failed: %s", download_path, exc)
            raise RetryableJobError(
                f"Download attachment {download_path} failed: {exc}",
                seconds=10,
            ) from exc
