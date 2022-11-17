## Manage Direct Messages

Direct Messages enable private conversations on Twitter. Direct Messages are one of the most popular features of Twitter, with a wide variety of use cases. These use cases range from group chats among friends, to powering customer support for brands around the world. New v2 versions of Direct Messages endpoints will be introduced in stages, and this first stage includes fundamental endpoints for creating Direct Messages and listing Direct Message conversation events. For the first time, the Twitter API v2 supports group conversations.

You can get more information for this at [docs](https://developer.twitter.com/en/docs/twitter-api/direct-messages/manage/introduction)


### Create a message in a 1-1 conversation with the participant

Creates a one-to-one Direct Message and adds it to the one-to-one conversation. 

This method either creates a new one-to-one conversation or retrieves the current conversation and adds the Direct Message to it.

```python
my_api.create_message_to_participant("1334059193268011010", text="dm by api")
# DirectMessageCreateResponse(dm_conversation_id='1301152652357595137-1334059193268011010', dm_event_id='1593234034146279428')
```

### Create a group conversation and add a DM to it

Creates a Direct Message on behalf of an authenticated user, and adds it to the specified conversation.

```python
my_api.create_message_to_conversation("1593091374437781506", text="message by api")
# DirectMessageCreateResponse(dm_conversation_id='1301152652357595137-1334059193268011010', dm_event_id='1593234034146279428')
```

### Adding a DM to an existing conversation (for both group and 1-1)

Creates a new group conversation and adds a Direct Message to it on behalf of an authenticated user.

```python
my_api.create_conversation(
    conversation_type="group", 
    message={"text": "hello"}, 
    participant_ids=["1334059193268011010", "906948460078698496"]
)
# DirectMessageCreateResponse(dm_conversation_id='1301152652357595137-1334059193268011010', dm_event_id='1593234034146279428')
```
