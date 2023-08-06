# Influence API

A python API for [Influence](https://influenceth.io).

## Development

You **must** have an API key from Influence to develop or use the API. Contact `DarkosNightmare#8555` on Discord, and request a production API key.

The preferred development environment is GitPod.

You will need the following environment variables defined to run unit tests:

- `INFLUENCE_CLIENT_ID`
- `INFLUENCE_CLIENT_SECRET`

Otherwise, tests relying on the live API will be skipped.

## Usage

```python
from influence_api import InfluenceClient

client = InfluenceClient(client_id="", client_secret="")

# Retrieve an asteroid
asteroid = client.get_asteroid(1)

# Retrieve a crew member
crewmember = client.get_crewmate(1)

# Use string options for key values (if applicable)
crewmember2 = client.get_crewmate(1, names=True)
```
