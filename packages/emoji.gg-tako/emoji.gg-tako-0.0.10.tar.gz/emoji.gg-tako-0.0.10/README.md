# (Unofficial) emoji.gg API Wrapper for Python | Documentation

## Installation:
To install with PIP, run this in your console:
```
pip install emoji.gg-tako
```
## Fetch Stats:

To fetch stats from [emoji.gg](https://emoji.gg):
```py
from emoji_gg import stats
...
await stats.fetch(endpoint)
```
Available Endpoints:
- emoji
- users
- faves
- pending

## Fetch Emoji:

To fetch emojis from [emoji.gg](https://emoji.gg):
```py
from emoji_gg import emoji
...
await emoji.fetch(option, query, endpoint) # endpoint is optional. if not provided, will return the whole JSON response.
```
Options:
- title
- id
- slug

Available Endpoints:
- title
- id
- slug
- image
- category
- license
- source
- faves
- author
