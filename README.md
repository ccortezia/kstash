# fdstash

A Python library for transparently linking large message attributes using remote object storage.

## Installation

```bash
pip install fdstash
```

## Requirements

- Python >= 3.13
- AWS credentials configured (for S3 storage)

## Quick Start

```python
# Optional: Test Backend Setup
import boto3
from moto import mock_aws
mock_aws().start()
conn = boto3.resource("s3", region_name="us-east-1")
conn.create_bucket(Bucket="stashes")
```

```python
import fdstash

# Process A: Sends a message containing the address of a stashed payload.
context = {"as_of": "today", "bin": b"0" * 1024 * 512}
stash = fdstash.create("context", context, namespace="stashes")
message = {"context": str(stash.address), "command": "gen_report"}  
assert str(stash.address) == "s3://stashes/context.c6ab205fe81dcad3eec3ab48b96b0618"

# Process B: Rebuilds the message from the stash's address.
loaded_stash = fdstash.retrieve(message["context"])
assert loaded_stash == stash
```

## Shared Links

Use `stash.share()` to produce a short-lived HTTPS link to the stash. 

See `fdstash.Config.share_ttl_sec` for configuration details.

```python
import time 

# Process A: Sends a message containing a shared link.
shared_link = stash.share(ttl_sec=5)

# Process B: Rebuilds the message from the shared link.
time.sleep(3)
loaded_stash = fdstash.retrieve(shared_link)
assert loaded_stash == shared_stash

# Process B: Fails to retrieve the stash from an expired link.
time.sleep(3)
loaded_stash = fdstash.retrieve(shared_link)
# Error: StashNotFound, share link expired
```

## Inline Data Optimization

`fdstash.create()` embeds small data in the stash's address.

See `fdstash.Config.max_inline_len` for configuration details.

```python
import fdstash
stash = fdstash.create("colorcode", 12, namespace="stashes")
assert str(stash.address) == "inline://stashes/colorcode?data=DA%3D%3D"
loaded_stash = fdstash.retrieve(stash.address)
assert loaded_stash == stash
loaded_stash.data
```

## Selectible Backends

Backends can be disabled to address specific deployment or test scenarios.

See `fdstash.Config.backends` for more details.

```python
import fdstash
config = fdstash.Config(backends=["mem"])
stash = fdstash.create("object", {"data": 123}, config=config)
assert str(stash.address) == "mem://default/object.34472d91b2f84052bf26d4eaa862ef86"
loaded_stash = fdstash.retrieve(stash.address, config=config)
assert loaded_stash == stash
```

### Development Setup

```bash
uv sync
source .venv/bin/activate
pytest
```