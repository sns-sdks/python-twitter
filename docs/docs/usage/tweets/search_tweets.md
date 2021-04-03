The recent and full-archive search REST endpoints are part of the Search Tweets group of endpoints, meaning they share a common design and features.

Search by recent tweets

```python
api.search_tweets(query="python")
# Response(data=[Tweet(id=1364512148865564675, text=RT @jesss_codes: Your resume: Git SSL Vue CSS...), Tweet(id=1364512106385702914, text=RT @theweeflea: Sturgeon goes on TV to declare...), Tweet(id=1364512102606467074, text=RT @tkEzaki:...), Tweet(id=1364512092343070721, text=RT @ore57436902: #Python #pyxel #ドルアーガの塔...), Tweet(id=1364512076601856007, text=RT @shosen_bt_pc:...), Tweet(id=1364512071866605568, text=RT @CatherineAdenle: 6 ways learning coding can...), Tweet(id=1364512071614889987, text=RT @giswqs: #geemap v0.8.11 has been released....), Tweet(id=1364512066770509824, text=RT @Akpanannang: Today when coming out from the...), Tweet(id=1364512053252284419, text=RT @HarbRimah: New Off-the-Shelf (OTS) Datasets...), Tweet(id=1364512030800171011, text=RT @gzadkowski: Day 5 - #100DaysOfCode...)])
```

Search by full-archive tweets, this api is `Academic Research product track only`.

```python
api.search_tweets(query="python", query_type="all")
# Response(data=[Tweet(id=1364512148865564675, text=RT @jesss_codes: Your resume: Git SSL Vue CSS...), Tweet(id=1364512106385702914, text=RT @theweeflea: Sturgeon goes on TV to declare...), Tweet(id=1364512102606467074, text=RT @tkEzaki:...), Tweet(id=1364512092343070721, text=RT @ore57436902: #Python #pyxel #ドルアーガの塔...), Tweet(id=1364512076601856007, text=RT @shosen_bt_pc:...), Tweet(id=1364512071866605568, text=RT @CatherineAdenle: 6 ways learning coding can...), Tweet(id=1364512071614889987, text=RT @giswqs: #geemap v0.8.11 has been released....), Tweet(id=1364512066770509824, text=RT @Akpanannang: Today when coming out from the...), Tweet(id=1364512053252284419, text=RT @HarbRimah: New Off-the-Shelf (OTS) Datasets...), Tweet(id=1364512030800171011, text=RT @gzadkowski: Day 5 - #100DaysOfCode...)])
```
