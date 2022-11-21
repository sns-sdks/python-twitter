# Changelog

All notable changes to this project will be documented in this file.

## [0.8.0](https://github.com/sns-sdks/python-twitter/v0.8.0) (2021-11-21)

### Features

- Add new fields for object update recently
- Add new apis for manage direct messages

## [0.7.9](https://github.com/sns-sdks/python-twitter/v0.7.9) (2021-09-20)

### Features

- Improve streaming api

### Fix

- Fix set error token after generate access token.


## [0.7.8](https://github.com/sns-sdks/python-twitter/v0.7.8) (2021-07-22)

### Features

- Support new query fields for get list tweets [#117](https://github.com/sns-sdks/python-twitter/issues/117)

## [0.7.7](https://github.com/sns-sdks/python-twitter/v0.7.7) (2021-05-23)

### Features

- New apis for get user timelines by reverse chronological.

## [0.7.6](https://github.com/sns-sdks/python-twitter/v0.7.6) (2021-04-07)

### Features

- New apis for bookmarks.
- New initial parameters `client secret` for `Confidential Clients`.

## [0.7.5](https://github.com/sns-sdks/python-twitter/v0.7.5) (2021-02-17)

### Features

- New api for get tweet quote tweets. [docs](https://twittercommunity.com/t/introducing-the-quote-tweets-lookup-endpoint-to-the-twitter-api-v2/168370)
- New update for spaces api. [docs](https://twittercommunity.com/t/bringing-tweets-shared-in-a-space-and-rsvp-count-to-the-spaces-endpoints/166746)

## [0.7.4](https://github.com/sns-sdks/python-twitter/v0.7.4) (2021-02-17)

### Features

- Add sort parameter for search tweets, [docs](https://twittercommunity.com/t/introducing-the-sort-order-parameter-for-search-endpoints-in-the-twitter-api-v2/166377)

## [0.7.3](https://github.com/sns-sdks/python-twitter/v0.7.3) (2021-01-24)

### Features

- Add parameters for pagination for tweet's liking users and retweets
- Add scripts for generate update text.

## [0.7.2](https://github.com/sns-sdks/python-twitter/v0.7.2) (2021-12-15)

### Features

- Add api for get authorized user data
- Refactor code for OAuth1

## [0.7.1](https://github.com/sns-sdks/python-twitter/v0.7.1) (2021-12-09)

### Features

- Add init parameters for oauth.

## [0.7.0](https://github.com/sns-sdks/python-twitter/v0.7.0) (2021-11-23)

### Features

- More apis for lists.

### Fix

- Fix manage_rules params [#94](https://github.com/sns-sdks/python-twitter/pull/94) By [@erwanvivien](https://github.com/erwanvivien).


## [0.6.1](https://github.com/sns-sdks/python-twitter/v0.6.1) (2021-11-15)

### Features

- Tweet Manage [#88](https://github.com/sns-sdks/python-twitter/issues/88)

### Fix

-  Fix ratelimt for some apis.


## [0.6.0](https://github.com/sns-sdks/python-twitter/v0.6.0) (2021-10-23)

### Features

- API for lists manage [#84](https://github.com/sns-sdks/python-twitter/issues/84)
- Tests on python 3.10

## [0.5.0](https://github.com/sns-sdks/python-twitter/v0.5.0) (2021-09-29)

### Features

- API for get user muting [#82](https://github.com/sns-sdks/python-twitter/issues/82)
- Beta OAuth2.0 auth flow [#80](https://github.com/sns-sdks/python-twitter/issues/80) 
- API for batch compliance [#76](https://github.com/sns-sdks/python-twitter/issues/76)

### Fix

- Fix rate limit 

## [0.4.2](https://github.com/sns-sdks/python-twitter/v0.4.2) (2021-08-21)

### Features

- API for new resource Space, lookup and search [#71](https://github.com/sns-sdks/python-twitter/issues/71)

### Fix

- Fix response data handler for streaming [#70](https://github.com/sns-sdks/python-twitter/issues/70)


## [0.3.5](https://github.com/sns-sdks/python-twitter/v0.3.5) (2021-08-12)

### Features

- API for manage retweets [#66](https://github.com/sns-sdks/python-twitter/issues/66)
- New field `alt_text` for Media [#68](https://github.com/sns-sdks/python-twitter/issues/68)


## [0.3.4](https://github.com/sns-sdks/python-twitter/v0.3.4) (2021-07-02)

### Features

- API for tweets counts [#58](https://github.com/sns-sdks/python-twitter/issues/58)
- New parameters for stream API [#60](https://github.com/sns-sdks/python-twitter/issues/60)
- API for mutes user [#61](https://github.com/sns-sdks/python-twitter/issues/61)


## [0.3.3](https://github.com/sns-sdks/python-twitter/v0.3.3) (2021-05-24)

### Features

- API for get blocking users.  [#52](https://github.com/sns-sdks/python-twitter/issues/52)
- API for user liked tweets and tweet liking users.  [#53](https://github.com/sns-sdks/python-twitter/issues/53)

### Broken Changes

- Refactor Ratelimit module.  [#54](https://github.com/sns-sdks/python-twitter/issues/54)


## [0.3.2](https://github.com/sns-sdks/python-twitter/v0.3.2) (2021-05-10)

### Features

- Model update for tweet and media


## [0.3.1](https://github.com/sns-sdks/python-twitter/v0.3.1) (2021-04-25)

### Features

- likes API
- keep uid with [`auth_user_id`](https://github.com/sns-sdks/python-twitter/pull/44)


## [0.3.0](https://github.com/sns-sdks/python-twitter/v0.3.0) (2021-04-08)

### Features

- Blocks API
- New Docs


### [0.2.0](https://github.com/sns-sdks/python-twitter/v0.2.0) (2021-03-13)

### Features

- Stream API


## [0.1.0](https://github.com/sns-sdks/python-twitter/v0.1.0) (2021-03-07)

### Features

- User Lookup
- User Follows
- Tweet Lookup
- Search Tweets
- Timelines
- Hide replies
