import logging
from struct import pack
import re
import base64
from pyrogram.file\_id import FileId
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor\_asyncio import AsyncIOMotorClient
from marshmallow\.exceptions import ValidationError
from info import FILE\_DB\_URL, FILE\_DB\_NAME, COLLECTION\_NAME, MAX\_RIST\_BTNS

logger = logging.getLogger(**name**)
logger.setLevel(logging.INFO)

client = AsyncIOMotorClient(FILE\_DB\_URL)
db = client\[FILE\_DB\_NAME]
instance = Instance.from\_db(db)

@instance.register
class Media(Document):
file\_id = fields.StrField(attribute='\_id')
file\_ref = fields.StrField(allow\_none=True)
file\_name = fields.StrField(required=True)
file\_size = fields.IntField(required=True)
file\_type = fields.StrField(allow\_none=True)
mime\_type = fields.StrField(allow\_none=True)
caption = fields.StrField(allow\_none=True)

```
class Meta:
    collection_name = COLLECTION_NAME
```

async def save\_file(media):
file\_id, file\_ref = unpack\_new\_file\_id(media.file\_id)
file\_name = re.sub(r"(\_|-|.|+)", " ", str(media.file\_name))
try:
file = Media(
file\_id=file\_id,
file\_ref=file\_ref,
file\_name=file\_name,
file\_size=media.file\_size,
file\_type=media.file\_type,
mime\_type=media.mime\_type
)
except ValidationError:
logger.exception('Error Occurred While Saving File In Database')
return False, 2
else:
try:
await file.commit()
except DuplicateKeyError:
logger.warning(str(getattr(media, "file\_name", "NO FILE NAME")) + " is already saved in database")
return False, 0
else:
logger.info(str(getattr(media, "file\_name", "NO FILE NAME")) + " is saved in database")
return True, 1

async def get\_search\_results(query, file\_type=None, max\_results=(MAX\_RIST\_BTNS), offset=0, filter=False):
query = query.strip()
if not query: raw\_pattern = '.'
elif ' ' not in query: raw\_pattern = r'(\b|\[.+-*])' + query + r'(\b|\[.+-*])'
else: raw\_pattern = query.replace(' ', r'.\*\[\s.+-\_]')
try: regex = re.compile(raw\_pattern, flags=re.IGNORECASE)
except: return \[], '', 0
filter = {'file\_name': regex}
if file\_type: filter\['file\_type'] = file\_type

```
total_results = await Media.count_documents(filter)
next_offset = offset + max_results
if next_offset > total_results: next_offset = ''

cursor = Media.find(filter)
# Sort by recent
cursor.sort('$natural', -1)
# Slice files according to offset and max results
cursor.skip(offset).limit(max_results)
# Get list of files
files = await cursor.to_list(length=max_results)
return files, next_offset, total_results
```

async def get\_file\_details(query):
filter = {'file\_id': query}
cursor = Media.find(filter)
filedetails = await cursor.to\_list(length=1)
return filedetails

def encode\_file\_id(s: bytes) -> str:
r = b""
n = 0
for i in s + bytes(\[22]) + bytes(\[4]):
if i == 0:
n += 1
else:
if n:
r += b"\x00" + bytes(\[n])
n = 0
r += bytes(\[i])
return base64.urlsafe\_b64encode(r).decode().rstrip("=")

def encode\_file\_ref(file\_ref: bytes) -> str:
return base64.urlsafe\_b64encode(file\_ref).decode().rstrip("=")

def unpack\_new\_file\_id(new\_file\_id):
"""Return file\_id, file\_ref"""
decoded = FileId.decode(new\_file\_id)
file\_id = encode\_file\_id(
pack(
"\<iiqq",
int(decoded.file\_type),
decoded.dc\_id,
decoded.media\_id,
decoded.access\_hash
)
)
file\_ref = encode\_file\_ref(decoded.file\_reference)
return file\_id, file\_ref
