# kstash

`kstash` converts payloads into addressable stashes. 

It allows programs to communicate using stash addresses instead of entire payloads, reducing the strain on messaging systems.

[![CI](https://github.com/ccortezia/kstash/actions/workflows/main.yml/badge.svg)](https://github.com/ccortezia/kstash/actions/workflows/main.yml)

## Installation

```bash
pip install kstash
```

## Requirements

- Python >= 3.13
- AWS credentials configured (for S3 storage)

## Basics

Use `kstash` to put a payload into an addressable stash.

Then provide `kstash` with the address to recover the payload.

```python
import kstash
stash = kstash.create("my-payload", "some-data")
loaded = kstash.retrieve(stash.address)
stash == loaded
```

## Simple Storage (S3)

By default, `kstash.create()` saves large payloads to S3.

```python
# Optional: Test Backend Setup
import boto3
from moto import mock_aws
mock_aws().start()
conn = boto3.resource("s3", region_name="us-east-1")
conn.create_bucket(Bucket="stashes")
```

```python
import kstash

# Process A: Sends a message containing the address of a stashed payload.
context = {"as_of": "today", "bin": b"0" * 1024 * 512}
stash = kstash.create("context", context, namespace="stashes")
message = {"context": str(stash.address), "command": "gen_report"}  
assert str(stash.address) == "s3://stashes/context.c6ab205fe81dcad3eec3ab48b96b0618"

# Process B: Rebuilds the message from the stash's address.
loaded_stash = kstash.retrieve(message["context"])
assert loaded_stash == stash
```

## Shared Links

Use `stash.share()` to produce a short-lived HTTPS link to the stash. 

See `kstash.Config.share_ttl_sec` for configuration details.

```python
import time 

# Process A: Sends a message containing a shared link.
shared_link = stash.share(ttl_sec=5)

# Process B: Rebuilds the message from the shared link.
time.sleep(3)
loaded_stash = kstash.retrieve(shared_link)
assert loaded_stash == shared_stash

# Process B: Fails to retrieve the stash from an expired link.
time.sleep(3)
loaded_stash = kstash.retrieve(shared_link)
# Error: StashNotFound, share link expired
```

## Inline Data Optimization

`kstash.create()` embeds small data in the stash's address.

See `kstash.Config.max_inline_len` for configuration details.

```python
import kstash
stash = kstash.create("colorcode", 12, namespace="stashes")
assert str(stash.address) == "inline://stashes/colorcode?data=DA%3D%3D"
loaded_stash = kstash.retrieve(stash.address)
assert loaded_stash == stash
loaded_stash.data
```

## Selectible Backends

Backends can be disabled to address specific deployment or test scenarios.

See `kstash.Config.backends` for more details.

```python
import kstash
config = kstash.Config(backends=["mem"])
stash = kstash.create("object", {"data": 123}, config=config)
assert str(stash.address) == "mem://default/object.34472d91b2f84052bf26d4eaa862ef86"
loaded_stash = kstash.retrieve(stash.address, config=config)
assert loaded_stash == stash
```

### Development Setup

```bash
uv sync
source .venv/bin/activate
pytest
```