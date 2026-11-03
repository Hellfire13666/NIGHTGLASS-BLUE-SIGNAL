#!/usr/bin/env python3
"""NIGHTGLASS Public Evidence Inspector v2.7.1.
One unauthenticated, user-requested Facebook HTML GET; no scraping of hidden data.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

VERSION = '2.7.1'
ALLOWED_HOSTS = {'facebook.com', 'www.facebook.com', 'm.facebook.com', 'web.facebook.com', 'mbasic.facebook.com', 'fb.watch'}
BYTE_LIMIT = 2 * 1024 * 1024
LOGIN_WORDS = ('log in', 'log into facebook', 'login', 'create new account', 'sign up')
PRIVATE_KEYS = re.compile(r'(?:access_token|token|cookie|password|session|secret|auth|key)', re.I)


def safe_url(raw):
    try:
        p = urllib.parse.urlsplit(raw)
        if p.scheme != 'https' or p.hostname not in ALLOWED_HOSTS or p.username or p.password or p.port not in (None, 443):
            return False
        if '\\' in raw or any(PRIVATE_KEYS.search(k) for k, _ in urllib.parse.parse_qsl(p.query, keep_blank_values=True)):
            return False
        return True
    except (ValueError, TypeError):
        return False


def scrub_url(raw):
    """Only trusted, nonsensitive query parameters are retained in reports."""
    p = urllib.parse.urlsplit(raw)
    keep = {'id', 'fbid', 'story_fbid', 'q'}
    query = urllib.parse.urlencode([(k, v) for k, v in urllib.parse.parse_qsl(p.query) if k in keep])
    return urllib.parse.urlunsplit((p.scheme, p.netloc, p.path, query, ''))


class BoundedRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, steps):
        self.steps = steps
        super().__init__()

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if len(self.steps) >= 4:
            raise ValueError('Redirect limit exceeded')
        if not safe_url(newurl):
            raise ValueError('Redirect to non-approved or credential-bearing URL blocked')
        self.steps.append({'status': int(code), 'host': urllib.parse.urlsplit(newurl).hostname,
                           'path': urllib.parse.urlsplit(newurl).path[:150]})
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = {}
        self.in_title = False
        self.title_parts = []
        self.anchors = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'title':
            self.in_title = True
        if tag == 'a' and a.get('href'):
            self.anchors += 1
        if tag == 'meta':
            name = a.get('property') or a.get('name')
            if name in ('og:title', 'og:description', 'og:type', 'og:url', 'description'):
                self.tags.setdefault(name, a.get('content', '')[:350])

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.in_title and sum(len(s) for s in self.title_parts) < 350:
            self.title_parts.append(data)


def kind_of(url):
    p = urllib.parse.urlsplit(url)
    path = p.path.rstrip('/').lower()
    if re.search(r'/groups/[^/]+/pending_posts/[^/]+', path):
        return 'GROUP PENDING-POST URL'
    if path.startswith('/share/p/'):
        return 'SHARED POST URL'
    if path.startswith('/share/r/') or path.startswith('/reel/'):
        return 'REEL URL'
    if re.search(r'/posts/[^/]+$', path) or path in ('/story.php', '/permalink.php'):
        return 'POST URL'
    if path.startswith('/search/'):
        return 'SEARCH URL'
    if path == '/profile.php':
        return 'PROFILE URL'
    if path.startswith('/groups/'):
        return 'GROUP URL'
    if path.startswith('/login') or path.startswith('/checkpoint'):
        return 'LOGIN OR CHECKPOINT URL'
    return 'OTHER FACEBOOK URL'


def inspect_html(html, source, final, redirects=(), status=200, truncated=False):
    parser = HeadParser()
    parser.feed(html)
    title = (parser.tags.get('og:title') or ''.join(parser.title_parts).strip())[:250]
    desc = (parser.tags.get('og:description') or parser.tags.get('description') or '')[:350]
    og_url = parser.tags.get('og:url', '')
    # URLs in OpenGraph descriptions may be useful, but are unverified text only.
    desc_url_match = re.search(r'https://(?:www\.|m\.)?facebook\.com/[^\s<>"\']+', desc)
    described_url = desc_url_match.group(0).rstrip('.,;') if desc_url_match else ''
    described_url = scrub_url(described_url) if described_url and safe_url(described_url) else ''
    lowered = html.lower()
    hints = any(word in lowered for word in LOGIN_WORDS)
    kind = kind_of(final)
    described_kind = kind_of(described_url) if described_url else 'NOT AVAILABLE'
    if kind == 'LOGIN OR CHECKPOINT URL':
        access = 'LOGIN/CHECKPOINT DESTINATION'
    elif described_kind == 'GROUP PENDING-POST URL':
        access = 'PENDING-POST REFERENCE; PUBLIC CONTENT NOT CONFIRMED'
    elif hints and parser.anchors == 0:
        access = 'POSSIBLE LOGIN-WALLED OR GENERIC RESPONSE'
    elif title or desc:
        access = 'PUBLIC METADATA PRESENT; POST CONTENT UNVERIFIED'
    else:
        access = 'NO USEFUL PUBLIC POST METADATA VERIFIED'
    return {
        'checked_utc': datetime.now(timezone.utc).isoformat(),
        'requested_url': scrub_url(source),
        'final_host': urllib.parse.urlsplit(final).hostname,
        'final_path': urllib.parse.urlsplit(final).path[:200],
        'http_status': status,
        'redirects': list(redirects),
        'source_type': kind_of(source),
        'final_type': kind,
        'description_link_type': described_kind,
        'description_link': described_url,
        'title': title,
        'description': desc,
        'open_graph_type': parser.tags.get('og:type', 'NOT AVAILABLE'),
        'anchor_links': parser.anchors,
        'login_hints': hints,
        'html_truncated': truncated,
        'access_assessment': access,
        'content_verified': False,
    }


def fetch(url, timeout=12):
    if not safe_url(url):
        raise ValueError('Only non-credential HTTPS Facebook URLs supported')
    redirects = []
    opener = urllib.request.build_opener(BoundedRedirect(redirects))
    req = urllib.request.Request(url, headers={'User-Agent': 'NIGHTGLASS-PublicEvidenceInspector/2.7.1', 'Accept': 'text/html'}, method='GET')
    with opener.open(req, timeout=timeout) as response:
        final = response.geturl()
        if not safe_url(final):
            raise ValueError('Final URL failed public-source safeguards')
        if 'text/html' not in response.headers.get('Content-Type', '').lower():
            raise ValueError('Non-HTML response, not inspected')
        raw = response.read(BYTE_LIMIT + 1)
        truncated = len(raw) > BYTE_LIMIT
        html = raw[:BYTE_LIMIT].decode('utf-8', 'replace')
        return inspect_html(html, url, final, redirects, getattr(response, 'status', 200), truncated)


def private_save(report):
    base = Path.home() / 'Documents' / 'NIGHTGLASS-VAULT' / 'evidence-inspector'
    base.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(base, 0o700)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    path = base / ('evidence-' + stamp + '.json')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='utf8') as file:
        json.dump(report, file, ensure_ascii=False, indent=2)
    return path


def show(report):
    print('NIGHTGLASS // PUBLIC EVIDENCE INSPECTOR v' + VERSION)
    print('[SOURCE TYPE]', report['source_type'])
    print('[HTTP]', report['http_status'], '| [REDIRECTS]', len(report['redirects']))
    print('[FINAL HOST]', report['final_host'])
    print('[FINAL TYPE]', report['final_type'])
    print('[TITLE]', report['title'] or 'NOT PROVIDED')
    print('[DESCRIPTION]', report['description'] or 'NOT PROVIDED')
    print('[DESCRIPTION LINK TYPE]', report['description_link_type'])
    if report['description_link']:
        print('[DESCRIPTION LINK]', report['description_link'])
    print('[OPEN GRAPH TYPE]', report['open_graph_type'])
    print('[ANCHOR LINKS]', report['anchor_links'])
    print('[LOGIN HINTS]', 'PRESENT' if report['login_hints'] else 'NOT DETECTED')
    print('[HTML]', 'TRUNCATED' if report['html_truncated'] else 'WITHIN LIMIT')
    print('[ASSESSMENT]', report['access_assessment'])
    print('[POST CONTENT] NOT VERIFIED')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Inspect one public Facebook link; no login or credentials')
    parser.add_argument('--url', required=True)
    parser.add_argument('--timeout', type=int, default=12)
    parser.add_argument('--save', action='store_true', help='Write metadata-only private JSON report')
    args = parser.parse_args(argv)
    try:
        if not 1 <= args.timeout <= 30:
            raise ValueError('Timeout must be 1–30 seconds')
        report = fetch(args.url, args.timeout)
        show(report)
        if args.save:
            print('[SAVED] Private report:', private_save(report).name)
        return 0
    except (ValueError, OSError, urllib.error.URLError, urllib.error.HTTPError) as err:
        print('[STOP] Public evidence inspection unavailable:', type(err).__name__)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
