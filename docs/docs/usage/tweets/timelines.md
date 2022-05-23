The user Tweet timeline endpoints provides access to Tweets published by a specific Twitter account.

Get user timelines

```python
api.get_timelines(user_id="2244994945")
# Response(data=[Tweet(id=1364275610764201984, text=If you're newly approved for the Academic...), Tweet(id=1362876655061073928, text=From our living rooms to yours 🐱‍💻🛋️Our...), Tweet(id=1362439338978467841, text=“To quote my creator Jerome Gangneux, I always...), Tweet(id=1362439338169016324, text=“In the 20th century, managers managed humans,...), Tweet(id=1362439336910675970, text=Meet one of the useful Twitter bots out there:...), Tweet(id=1359912509940011010, text=Valentine’s Day is approaching! 💙 Over the...), Tweet(id=1359554366051504129, text=Go ahead, follow another puppy account. We...), Tweet(id=1357371424487268354, text=Learn how academics can get historical Tweets...), Tweet(id=1356991771553583106, text=Who knew an API could be delicious?...), Tweet(id=1354215875998437376, text=RT @TwitterOSS: Today we’re happy to share...)])
```

Get collection of the most recent Tweets and Retweets posted by you and users you follow

```python
my_api.get_timelines_reverse_chronological(user_id="2244994945")
# Response(data=[Tweet(id=1524796546306478083, text=Today marks the launch of Devs in the Details...), Tweet(id=1524468552404668416, text=📢 Join @jessicagarson @alanbenlee and @i_am_daniele tomorrow...))
```

Get tweets which mention target user

```python
api.get_mentions(user_id="2244994945")
# Response(data=[Tweet(id=1364407587207213056, text=@scottmathson @TwitterDev What would you want...), Tweet(id=1364398068313903104, text=@Twitter should consider supporting...), Tweet(id=1364377794327633925, text=@sugan2424 @TwitterDev @threadreaderapp You...), Tweet(id=1364377404156772352, text=@TwitterDev What kind of tweet / attachment is...), Tweet(id=1364373969852366849, text=• Thirdly, that @Twitter, @Twittersafety,...), Tweet(id=1364367885582352386, text=@Twitter @TwitterSafety @TwitterDev @jack...), Tweet(id=1364366114998870016, text=I have mixed feelings about @Twitter /...), Tweet(id=1364364744916951040, text=@Casanovacane @jack @TwitterDev can we get a...), Tweet(id=1364359199795240961, text=@TwitterDev @suhemparack A Blue app going to...), Tweet(id=1364338409494503425, text=@FairyMaitre @TwitterDev tkt)])
```
