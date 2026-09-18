"""Shared configuration and API transport. No implicit task creation or key logging."""
import json
import os
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

DEFAULTS = {
    'base_url': 'https://api.v2fun.art/api/v1', 'model': 'pro',
    'with_texture': True, 'pbr_texture': True, 'hd_texture': True,
    'concurrency': 1, 'poll_seconds': 15,
}


def config_path(project, explicit=None):
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if not path.is_file():
            raise ValueError('Explicit configuration does not exist')
        return path
    project = Path(project).resolve()
    for path in [project / '.v2fun/config.json', project.parent / 'v2fun.local.yaml']:
        if path.is_file():
            return path
    return None


def load_config(project, explicit=None):
    path = config_path(project, explicit)
    config = dict(DEFAULTS)
    if path:
        try:
            values = json.loads(path.read_text())
        except (ValueError, UnicodeError):
            raise ValueError('Configuration must contain a JSON object') from None
        if not isinstance(values, dict):
            raise ValueError('Configuration must contain a JSON object')
        config.update(values)
    return config


def api_key(config):
    key = os.environ.get('V2FUN_API_KEY') or config.get('api_key')
    if not isinstance(key, str) or not key.strip():
        raise ValueError('Missing V2FUN_API_KEY; configure the current environment or an explicit local config')
    return key.strip()


class Client:
    def __init__(self, config, opener=None):
        self.base = config['base_url'].rstrip('/')
        parsed = urlsplit(self.base)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError('API base_url must be an HTTPS origin/path without credentials or query')
        self.key = api_key(config)
        self.open = opener or urlopen

    def request(self, endpoint, payload=None):
        if not endpoint.startswith('/') or endpoint.startswith('//') or '?' in endpoint or '#' in endpoint:
            raise ValueError('Expected an API-relative endpoint')
        request = Request(self.base + endpoint,
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={'Authorization': 'Bearer ' + self.key, 'Content-Type': 'application/json'})
        # POSTs are never retried here: the executor owns reservation and recovery.
        with self.open(request, timeout=120) as response:
            return json.load(response)

    def download(self, url):
        if urlsplit(url).scheme != 'https':
            raise ValueError('Download must use HTTPS')
        # Signed asset hosts never receive API credentials.
        with self.open(url, timeout=180) as response:
            return response.read()
