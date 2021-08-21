The Spaces lookup endpoints help you lookup live or scheduled Spaces, and enable you to build discovery experiences to give your users ways to find Spaces they may be interested in.
You can get more information at [Lookup docs](https://developer.twitter.com/en/docs/twitter-api/spaces/lookup/introduction).

There have multiple methods for get spaces data by api.

## Get space by space ID

```python
api.get_space(space_id="1DXxyRYNejbKM")
# Response(data=[Space(id='1DXxyRYNejbKM', state='live')])
```

## Get spaces by multi spaces IDs

```python
api.get_spaces(space_ids=["1DXxyRYNejbKM", "1nAJELYEEPvGL"])
# Response(data=[Space(id='1DXxyRYNejbKM', state='live'), Space(id='1nAJELYEEPvGL', state='live')])
```

## Get spaces by multi creator IDs

```python
api.get_spaces_by_creator(creator_ids=["2244994945", "6253282"])
# Response(data=[Space(id='1DXxyRYNejbKM', state='live'), Space(id='1nAJELYEEPvGL', state='live')])
```