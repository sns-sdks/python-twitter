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
        url=f"https://api.twitter.com/2/dm_conversations/dm_events",
        json=events_data,
    )

    resp = api_with_user.get_dm_events(
        dm_event_fields="id,text,event_type,dm_conversation_id,created_at,sender_id,attachments,participant_ids,referenced_tweets",
    )
    assert resp.data[0].dm_conversation_id == "1585094756761149440"
