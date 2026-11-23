"""Audit staged files and reachable commits without printing sensitive values."""
from pathlib import Path
import argparse
import csv
import io
import math
import re
import subprocess
import sys
import tokenize

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = frozenset({
    '.gitattributes', '.gitignore', '.github/workflows/validate.yml',
    'README.md', 'PRIVACY.md', 'requirements.txt',
    'docs/methods.md', 'docs/manuscript.md',
    'methods/__init__.py', 'methods/projection.py', 'methods/dynamics.py',
    'methods/hypergraph.py', 'methods/estimation.py', 'methods/demo.py',
    'tests/test_principles.py', 'tests/test_release.py', 'tools/check_release.py',
    'docs/results.md', 'results/seeg_paired_orders.csv',
    'results/seeg_candidate_curves.csv', 'results/seeg_order_summary.csv',
    'results/seeg_paired_summary.csv', 'results/seeg_participant_summary.csv',
})
RESULT_SCHEMAS = {
    'results/seeg_paired_orders.csv': 'record_code participant_code receiver_index low_q high_q low_joint high_joint both_joint different_q joint_different bootstrap_joint_difference_fraction',
    'results/seeg_candidate_curves.csv': 'record_code participant_code receiver_index state q selected risk_over_C benefit_pct',
    'results/seeg_order_summary.csv': 'selected_q n compression task joint compression_only compression_fail',
    'results/seeg_paired_summary.csv': 'low_q high_q total both_joint',
    'results/seeg_participant_summary.csv': 'participant_code n record_count reduced_joint retained_joint other',
}
PATTERNS = (
    ('record identifier', re.compile(r'\b(?:P|S|G)\d{2,}\b')),
    ('clinical identifier field', re.compile(r'\b(?:patient|subject|recording)[_-](?:id|name)\b', re.I)),
    ('mail address', re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')),
    ('access credential', re.compile(r'\bgh[pousr]_[A-Za-z0-9]{20,}')),
    ('access credential', re.compile(r'\bgithub_pat_[A-Za-z0-9_]{20,}')),
    ('private key', re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----')),
    ('local path', re.compile(r'\b[A-Za-z]:[\\/](?:Users|wcl|clinical|data)[\\/]', re.I)),
    ('local path', re.compile(r'/(?:home|Users)/[A-Za-z0-9_.-]+/')),
    ('encoded payload', re.compile(r'[A-Za-z0-9+/]{256,}={0,2}')),
)


def validate_result(path, content):
    """Accept reviewed statistics only, never free-text clinical fields."""
    try:
        reader = csv.DictReader(io.StringIO(content), strict=True)
        if reader.fieldnames != RESULT_SCHEMAS[path].split():
            return ['unapproved result schema']
        count = 0
        for row in reader:
            count += 1
            if None in row or any(v is None for v in row.values()):
                return ['malformed result row']
            for key, value in row.items():
                if key in ('record_code', 'participant_code'):
                    prefix = 'S' if key == 'record_code' else 'P'
                    valid = re.fullmatch(prefix + r'[0-9]{2}', value) is not None
                elif key == 'state':
                    valid = value in ('low', 'high')
                elif key in ('low_joint', 'high_joint', 'different_q', 'joint_different', 'selected') or (key == 'both_joint' and path.endswith('paired_orders.csv')):
                    valid = value in ('True', 'False')
                elif key in ('risk_over_C', 'benefit_pct', 'bootstrap_joint_difference_fraction'):
                    number = float(value)
                    valid = math.isfinite(number)
                    if key == 'risk_over_C':
                        valid = valid and number >= 0
                    if key == 'bootstrap_joint_difference_fraction':
                        valid = valid and 0 <= number <= 1
                else:
                    valid = re.fullmatch(r'[0-9]+', value) is not None
                    if valid and key in ('q', 'selected_q', 'low_q', 'high_q'):
                        valid = 1 <= int(value) <= 4
                    if valid and key in ('receiver_index', 'record_count'):
                        valid = int(value) >= 1
                if not valid:
                    return ['unapproved result value']
        return [] if count else ['empty result table']
    except (csv.Error, ValueError, OverflowError):
        return ['malformed result table']


def validate_blob(path, data, mode='100644'):
    """Return issue categories only; never include matched content in logs."""
    issues = []
    if path not in ALLOWED:
        issues.append('path outside reviewed allowlist')
    if mode not in ('100644', '100755'):
        issues.append('non-regular file')
    if len(data) > 100_000:
        issues.append('oversized text asset')
    if b'\0' in data or data.startswith((b'PK\x03\x04', b'\x1f\x8b', b'%PDF', b'\x89PNG')):
        issues.append('binary or archive payload')
    try:
        content = data.decode('utf-8')
    except UnicodeDecodeError:
        return issues + ['non-UTF-8 content']
    if path in RESULT_SCHEMAS:
        issues.extend(validate_result(path, content))
    mail_content = content
    if path.endswith('.py'):
        # Matrix multiplication in Python is not an email address. Credentials
        # and contact strings can still occur in literals or comments.
        try:
            mail_content = '\n'.join(t.string for t in tokenize.generate_tokens(io.StringIO(content).readline)
                                     if t.type in (tokenize.STRING, tokenize.COMMENT))
        except (tokenize.TokenError, IndentationError):
            pass
    for label, pattern in PATTERNS:
        if label == 'record identifier' and path in RESULT_SCHEMAS:
            # P/S labels are permitted only in fixed, type-checked code columns.
            continue
        if pattern.search(mail_content if label == 'mail address' else content):
            issues.append(label)
    return list(dict.fromkeys(issues))


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, stderr=subprocess.PIPE)


def audit(include_history=False):
    checked = set()
    issues = []

    def check(mode, oid, path):
        key = (mode, oid, path)
        if key in checked:
            return
        checked.add(key)
        # A submodule object is not a blob and must be rejected without reading it.
        if mode not in ('100644', '100755'):
            issues.append((path, ['non-regular file']))
            return
        found = validate_blob(path, git('cat-file', 'blob', oid), mode)
        if found:
            issues.append((path, found))

    staged = git('ls-files', '--stage', '-z')
    staged_paths = set()
    for entry in staged.split(b'\0'):
        if not entry:
            continue
        meta, path_raw = entry.split(b'\t', 1)
        mode, oid, stage = meta.decode().split()
        path = path_raw.decode('utf-8')
        staged_paths.add(path)
        if stage != '0':
            issues.append((path, ['unmerged entry']))
        check(mode, oid, path)
    if not staged_paths:
        issues.append(('<index>', ['empty index']))
    for required in ALLOWED - staged_paths:
        issues.append((required, ['required reviewed file missing']))

    commits = []
    if include_history:
        commits = git('rev-list', '--all').decode().splitlines()
        for commit in commits:
            for entry in git('ls-tree', '-r', '-z', commit).split(b'\0'):
                if not entry:
                    continue
                meta, path_raw = entry.split(b'\t', 1)
                mode, _, oid = meta.decode().split()
                check(mode, oid, path_raw.decode('utf-8'))
    return issues, len(checked), len(commits)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--history', action='store_true')
    args = parser.parse_args()
    try:
        issues, blobs, commits = audit(args.history)
    except (subprocess.CalledProcessError, UnicodeError, ValueError):
        print('Release audit could not inspect the Git index or history.', file=sys.stderr)
        return 2
    if issues:
        # File names can themselves contain identifiers. Print counts and categories only.
        labels = sorted({label for _, found in issues for label in found})
        print(f'Release audit failed: {len(issues)} entries; categories: {", ".join(labels)}', file=sys.stderr)
        return 1
    print(f'Release audit passed: {blobs} reviewed blob/path entries; {commits} reachable commits.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
