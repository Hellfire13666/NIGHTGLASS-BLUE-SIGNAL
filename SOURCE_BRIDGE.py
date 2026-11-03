"""Offline source bridge for user-provided permitted CSV/JSON/JSONL exports."""
from pathlib import Path
import csv, json, hashlib, datetime

MAX_BYTES=25*1024*1024
ALLOWED={'.csv','.json','.jsonl'}

def inspect_source(value):
    """Inspect a local export without printing record content or identifying information."""
    path=Path(value).expanduser()
    if not path.is_file() or path.suffix.lower() not in ALLOWED:
        raise ValueError('Expected an existing CSV, JSON or JSONL file')
    size=path.stat().st_size
    if size>MAX_BYTES:raise ValueError('File exceeds 25 MiB inspection limit')
    raw=path.read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    try:text=raw.decode('utf-8-sig')
    except UnicodeError as e:raise ValueError('File must be UTF-8') from e
    ext=path.suffix.lower()
    if ext=='.csv':
        reader=csv.DictReader(text.splitlines())
        if not reader.fieldnames:raise ValueError('CSV requires a header')
        count=sum(1 for row in reader if any(v for v in row.values()))
        fields=[str(x) for x in reader.fieldnames]
    elif ext=='.jsonl':
        count=0; fields=set()
        for line in text.splitlines():
            if not line.strip():continue
            obj=json.loads(line)
            if not isinstance(obj,dict):raise ValueError('JSONL must contain objects')
            count+=1;fields.update(obj.keys())
        fields=sorted(str(x) for x in fields)
    else:
        obj=json.loads(text)
        if isinstance(obj,list):records=obj
        elif isinstance(obj,dict):
            records=next((obj[k] for k in ('records','comments','data') if isinstance(obj.get(k),list)),None)
            if records is None:raise ValueError('JSON must contain a list or records/comments/data list')
        else:raise ValueError('JSON requires an array or object with records')
        if any(not isinstance(r,dict) for r in records):raise ValueError('JSON records must be objects')
        count=len(records);fields=sorted({str(k) for r in records for k in r})
    if count>100000:raise ValueError('Inspection limit is 100,000 records')
    recognized=bool(set(fields)&{'id','comment_id','message','text','author','name','created_time','timestamp'})
    return {'format':ext[1:].upper(),'bytes':size,'records':count,'sha256':digest,'schema_detected':recognized,
            'field_count':len(fields),'source_mode':'USER PROVIDED · OFFLINE · UNVERIFIED',
            'inspected_utc':datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}

def render_summary(info):
    return ('◆ SOURCE BRIDGE / OFFLINE INSPECTION\n'
            +f"FORMAT: {info['format']}  |  RECORDS: {info['records']}  |  SIZE: {info['bytes']} bytes\n"
            +f"FIELDS: {info['field_count']}  |  RECOGNIZED SCHEMA: {'YES' if info['schema_detected'] else 'UNKNOWN'}\n"
            +f"SHA-256: {info['sha256']}\n"
            +'SOURCE: USER-PROVIDED FILE  |  NOT VERIFIED FACEBOOK DATA  |  NO NETWORK')
