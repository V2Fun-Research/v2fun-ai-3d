"""V2Fun CN/global routing. Read-only discovery; task bindings never fail over."""
import hashlib
import json
import math
import os
import re
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

SERVERS = {
    'cn': {'base_url': 'https://api.v2fun.art/api/v1', 'docs_base_url': 'https://doc.v2fun.art'},
    'global': {'base_url': 'https://api.v2fun.ai/api/v1', 'docs_base_url': 'https://doc.v2fun.ai'},
}
DEFAULTS = {'region': 'auto', 'model': 'pro', 'with_texture': True,
            'pbr_texture': True, 'hd_texture': True, 'concurrency': 1, 'poll_seconds': 15}

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Never forward credentials or replay a POST through a redirect.


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


def load_config(project, explicit=None, region=None):
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
    selections = [v for v in [region, os.environ.get('V2FUN_REGION'), config.get('region')] if v and v != 'auto']
    if any(v not in SERVERS for v in selections) or len(set(selections)) > 1:
        raise ValueError('Invalid or conflicting region; use cn, global or auto and reconcile configuration')
    config['region'] = selections[0] if selections else 'auto'
    config['_project'] = str(Path(project).resolve())
    selected_region(config)  # Validate host/region conflicts even in offline doctor.
    return config


def selected_region(config):
    region = config.get('region', 'auto')
    if region not in {'auto', *SERVERS}:
        raise ValueError('Region must be cn, global or auto')
    base = config.get('base_url')
    if base:
        matching = [r for r, s in SERVERS.items() if s['base_url'] == base.rstrip('/')]
        if not matching:
            raise ValueError('API base_url must match an official CN/global host')
        if region != 'auto' and region != matching[0]:
            raise ValueError('Configured region conflicts with base_url')
        region = matching[0]
    docs = config.get('docs_base_url')
    if docs and (region == 'auto' or docs.rstrip('/') != SERVERS[region]['docs_base_url']):
        raise ValueError('Configured documentation host conflicts with region')
    return region


def api_key(config):
    value = os.environ.get('V2FUN_API_KEY') or config.get('api_key')
    if not isinstance(value, str):
        raise ValueError('Missing V2FUN_API_KEY; configure environment or an explicit local config')
    value = re.sub(r'^Authorization\s*:\s*', '', value.strip(), flags=re.I)
    value = re.sub(r'^Bearer\s+', '', value, flags=re.I).strip()
    if not value or re.search(r'\s', value) or value.upper() in {'YOUR_API_KEY', '$YOUR_API_KEY', '<YOUR_API_KEY>', 'BEARER'}:
        raise ValueError('Supply a real API key or one Bearer header, without whitespace or placeholders')
    return value


def fingerprint(key):
    return hashlib.sha256(('v2fun-routing-v1:' + key).encode()).hexdigest()


def validate_balance(value):
    balance = value.get('balance') if isinstance(value, dict) else None
    if type(balance) not in (float, int) or not math.isfinite(balance):
        raise ValueError('Balance response has an unknown schema')
    return balance


class Client:
    def __init__(self, config, opener=None, binding=None):
        self.config = config
        self.key = api_key(config)
        self.open = opener or build_opener(NoRedirect()).open
        self.credential = fingerprint(self.key)
        self.cache_path = Path(config['_project']) / '.v2fun/server.json' if config.get('_project') else None
        explicit = selected_region(config)
        if binding is not None:
            self.bind(binding, explicit)
        else:
            cached = None
            if self.cache_path and self.cache_path.exists():
                try:
                    cached = json.loads(self.cache_path.read_text())
                except (OSError, ValueError):
                    raise ValueError('Unreadable server binding; inspect project .v2fun/server.json') from None
            if cached and cached.get('credential_fingerprint') == self.credential:
                self.bind(cached, explicit)
                self.balance = validate_balance(self.request('/balance'))
            else:
                self.resolve(explicit)
            self.save_binding()

    def bind(self, binding, explicit='auto'):
        region = binding.get('region')
        if region not in SERVERS or binding.get('base_url') != SERVERS[region]['base_url']:
            raise ValueError('Task/quote has no valid server binding; explicitly migrate its original server before recovery')
        if binding.get('docs_base_url') != SERVERS[region]['docs_base_url']:
            raise ValueError('Task/quote documentation host conflicts with region')
        if explicit != 'auto' and explicit != region:
            raise ValueError('Configured server conflicts with saved task/quote; never move a task between servers')
        if binding.get('credential_fingerprint') != self.credential:
            raise ValueError('Credentials differ from saved task/quote; verify account and migrate binding explicitly')
        self.region = region
        self.base = SERVERS[region]['base_url']

    def resolve(self, explicit):
        outcomes = {}
        candidates = [explicit] if explicit != 'auto' else list(SERVERS)
        for region in candidates:
            try:
                result = self._request(SERVERS[region]['base_url'], '/balance')
                outcomes[region] = ('valid', validate_balance(result))
            except HTTPError as exc:
                # A 403 is a scope problem, not proof that the key belongs elsewhere.
                outcomes[region] = ('unauthorized' if exc.code == 401 else 'inconclusive', None)
            except (URLError, OSError, ValueError):
                outcomes[region] = ('inconclusive', None)
        valid = [r for r, result in outcomes.items() if result[0] == 'valid']
        if len(valid) == 2:
            raise ValueError('Key works on both servers; select V2FUN_REGION=cn or global')
        if any(result[0] == 'inconclusive' for result in outcomes.values()):
            raise ValueError('Server identification incomplete (network, permission, rate limit or response schema); select/verify a server, do not fail over')
        if len(valid) != 1:
            raise ValueError('API key was not accepted by the selected server(s); check credentials and region')
        self.region = valid[0]
        self.base = SERVERS[self.region]['base_url']
        self.balance = outcomes[self.region][1]

    def binding(self):
        return {'region': self.region, **SERVERS[self.region], 'credential_fingerprint': self.credential}

    def save_binding(self):
        if self.cache_path:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            # Cache only routing + one-way credential identity; never the API key.
            temp = self.cache_path.with_name('server.' + str(os.getpid()) + '.tmp')
            fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, 'w') as stream:
                json.dump({**self.binding(), 'verified_at': time.time()}, stream, indent=2)
            temp.replace(self.cache_path)

    def _request(self, base, endpoint, payload=None):
        if not endpoint.startswith('/') or endpoint.startswith('//') or '?' in endpoint or '#' in endpoint or '\\' in endpoint or '..' in endpoint:
            raise ValueError('Expected an API-relative endpoint')
        request = Request(base + endpoint,
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={'Authorization': 'Bearer ' + self.key, 'Content-Type': 'application/json'})
        with self.open(request, timeout=30 if payload is None else 120) as response:
            return json.load(response)

    def request(self, endpoint, payload=None):
        return self._request(self.base, endpoint, payload)

    def download(self, url):
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError('Download must use HTTPS without URL credentials')
        with self.open(url, timeout=180) as response:
            return response.read()  # No API Authorization header on signed downloads.
