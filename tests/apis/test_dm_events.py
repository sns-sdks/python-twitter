"""
    tests for dm events
"""
import responses


@responses.activate
def test_get_dm_events_by_participant(api_with_user, helpers):
    events_data = helpers.load_json_data(
        "testdata/apis/dm_events/events_by_participant.json"
    )
    participant_id = "906948460078698496"

    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/dm_conversations/with/{participant_id}/dm_events",
        json=events_data,
    )

    resp = api_with_user.get_dm_events_by_participant(
        participant_id=participant_id,
        dm_event_fields="id,text,event_type,dm_conversation_id,created_at,sender_id,attachments,participant_ids,referenced_tweets",
    )
    assert resp.data[0].id == "1585321444547837956"


@responses.activate
def test_get_dm_events_by_conversation(api_with_user, helpers):
    events_data = helpers.load_json_data(
        "testdata/apis/dm_events/events_by_conversation.json"
    )
    dm_conversation_id = "1585094756761149440"

    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/dm_conversations/{dm_conversation_id}/dm_events",
        json=events_data,
    )

    resp = api_with_user.get_dm_events_by_conversation(
        dm_conversation_id=dm_conversation_id,
        dm_event_fields="id,text,event_type,dm_conversation_id,created_at,sender_id,attachments,participant_ids,referenced_tweets",
    )
    assert resp.data[0].dm_conversation_id == "1585094756761149440"


@responses.activate
def test_get_dm_events(api_with_user, helpers):
    events_data = helpers.load_json_data("testdata/apis/dm_events/events.json")

    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/dm_events",
        json=events_data,
    )

    resp = api_with_user.get_dm_events(
        dm_event_fields="id,text,event_type,dm_conversation_id,created_at,sender_id,attachments,participant_ids,referenced_tweets",
    )
    assert resp.data[0].dm_conversation_id == "1585094756761149440"


@responses.activate
def test_create_message_to_participant(api_with_user, helpers):
    data = helpers.load_json_data("testdata/apis/dm_events/events_create.json")
    participant_id = "1234567"

    responses.add(
        responses.POST,
        url=f"https://api.twitter.com/2/dm_conversations/with/{participant_id}/messages",
        json=data,
    )
    resp = api_with_user.create_message_to_participant(
        participant_id=participant_id,
        text="hello",
        attachments=[{"media_id": "1455952740635586573"}],
    )
    assert resp.dm_conversation_id == "1346889436626259968"


@responses.activate
def test_create_message_to_conversation(api_with_user, helpers):
    data = helpers.load_json_data("testdata/apis/dm_events/events_create.json")
    dm_conversation_id = "7654321"

    responses.add(
        responses.POST,
        url=f"https://api.twitter.com/2/dm_conversations/{dm_conversation_id}/messages",
        json=data,
    )
    resp = api_with_user.create_message_to_conversation(
        dm_conversation_id=dm_conversation_id,
        text="hello",
        attachments=[{"media_id": "1455952740635586573"}],
    )
    assert resp.dm_conversation_id == "1346889436626259968"


@responses.activate
def test_create_conversation(api_with_user, helpers):
    data = helpers.load_json_data("testdata/apis/dm_events/events_create.json")
    responses.add(
        responses.POST,
        url=f"https://api.twitter.com/2/dm_conversations",
        json=data,
    )
    resp = api_with_user.create_conversation(
        conversation_type="group",
        message={"text": "hello"},
        participant_ids=["1234567", "7654321"],
    )
    assert resp.dm_conversation_id == "1346889436626259968"
