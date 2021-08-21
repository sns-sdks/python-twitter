This endpoint allows you to search Spaces by their title, and to filter results by status. This endpoint is useful to discover live or upcoming Spaces based on keywords, mentioned users or hashtags in their title.

The endpoint accepts one or more keywords as a query. Its results can be filtered by the status of a Space (live or scheduled). By default, a request will return both live and scheduled Spaces that match the specified query.

You can get more information at [search docs](https://developer.twitter.com/en/docs/twitter-api/spaces/search/introduction).

## Search spaces

```python
api.search_spaces(query="hello", state="live")
# Response(data=[Space(id='1yoKMAybPkjKQ', state='live')])
```
