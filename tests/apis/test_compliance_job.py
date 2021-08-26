"""
    Tests for compliance jobs api.
"""

import pytest
import responses


@responses.activate
def test_get_compliance_job(api, helpers):
    job_id = "1423095206576984067"

    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/compliance/jobs/{job_id}",
        json=helpers.load_json_data("testdata/apis/compliance_jobs/job_resp.json"),
    )

    resp = api.get_compliance_job(job_id=job_id)
    assert resp.data.id == job_id


@responses.activate
def test_get_compliance_jobs(api, helpers):
    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/compliance/jobs",
        json=helpers.load_json_data("testdata/apis/compliance_jobs/jobs_resp.json"),
    )

    resp = api.get_compliance_jobs(job_type="tweets", status="complete")
    assert resp.data[0].id == "1421185651106480129"
    assert len(resp.data) == 2


@responses.activate
def test_create_compliance_job(api, helpers):
    responses.add(
        responses.POST,
        url=f"https://api.twitter.com/2/compliance/jobs",
        json=helpers.load_json_data(
            "testdata/apis/compliance_jobs/create_job_resp.json"
        ),
    )

    job = api.create_compliance_job(job_type="tweets")
    assert job.id == "1423691444842209280"
    assert job.status == "created"

    resp_json = api.create_compliance_job(
        job_type="tweets", name="test-job", resumable=False, return_json=True
    )
    assert resp_json["data"]["status"] == "created"
