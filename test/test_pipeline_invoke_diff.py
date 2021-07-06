import pytest
import requests
import json
import os

GIS_FUNCTION_HOST = 'http://localhost:3000'


#
# Test utils
#

def get_workspace_access_token(workspace_id):
    """
    NOTE: you must have exported your access token to workspaces you want to used in tests that use this function
    (after any minus signs in the workspace_id have been replaced with underscores) via

        export RISK_STREAM_ACCESS_TOKEN_my_cytora_workspace=<access_token_string>

    """
    access_token_env_var = f"RISK_STREAM_ACCESS_TOKEN_{workspace_id.replace('-', '_')}"
    return os.environ.get(access_token_env_var)


def remove_predicted_fields(fields):
    filtered_fields = []
    for field in fields:
        if not field.get('name_entity').endswith('.predicted'):
            filtered_fields.append(field)
    return filtered_fields


def sort_evaluated_field_ids(segment_tagger_results):
    for segment_tagger_result in segment_tagger_results:
        segment_tagger_result['evaluatedFieldIds'] = sorted(segment_tagger_result['evaluatedFieldIds'])
    return segment_tagger_results


#
# Automated regression tests
#

# The parametrize fixture runs the test_pipeline_invoke_diff function once for every entry in argvalues
@pytest.mark.parametrize(
    argnames="workspace_id,pipeline_id,invocation_id",
    argvalues=[
        ('ingest-cytora', 'cytora-dev-submission-ingestion-data-attributes', '55830088-b166-49d5-997d-072095af79a4'),
        ('ingest-cytora', 'cytora-dev-submission-ingestion-extractions', '9d6333e7-7c9d-4247-9608-5e065657cf76'),
    ]
)
def test_pipeline_invoke_diff(workspace_id, pipeline_id, invocation_id):
    """
    The purpose of this automated regression test, is to make sure the currently proposed code changes, still produce
    the same output that the (usually older) code version that has produced a specified invocation_id. It is meant to
    act as an automated regression test, with a human in the loop to decide if identified differences are expected or
    not. When running in PyCharm, a handy link called <Click to see difference> is offered between the actual and
    the expected values, which when clicked opens a visualisation of the diff (which helps to identify if differences
    are expected or not.)
    """
    workspace_access_token = get_workspace_access_token(workspace_id)

    # Get the previous invocation with invocation_id
    previous_invocation = requests.get(
        url=f'{RISK_STREAM_HOST}/{workspace_id}/pipeline/{pipeline_id}/invocation/{invocation_id}',
        headers={
            'Authorization': f'Bearer {workspace_access_token}'
        }
    ).json()
    # Get the field and segment outputs we got last time for invocation_id
    previous_fields_response = remove_predicted_fields(previous_invocation['fields_response'])
    previous_segment_tagger_results = sort_evaluated_field_ids(previous_invocation.get('segment_tagger_results', []))

    # Get the input and config that was used for invocation_id
    previous_invocation_pipeline_config = previous_invocation['pipeline_config']
    previous_invocation_record_raw_binary = requests.get(
        url=previous_invocation['record_raw_blob_url'],
    ).content

    # Perform an ad-hoc (not stored) pipeline invocation with the same input and config
    new_invocation = requests.put(
        url=f'{RISK_STREAM_HOST}/{workspace_id}/pipeline/invoke',
        params={
            'pipelineConfig': json.dumps(previous_invocation_pipeline_config)
        },
        headers={
            'Authorization': f'Bearer {workspace_access_token}'
        },
        data=previous_invocation_record_raw_binary
    ).json()

    # Get the fields and segments created by the new ad-hoc invocation
    current_fields_response = remove_predicted_fields(new_invocation['response'])
    current_segment_tagger_results = sort_evaluated_field_ids(new_invocation.get('segment_tagger_results', []))

    # We expect the new code to create the same fields and segments as the code that produced the old invocation_id
    assert current_fields_response == previous_fields_response
    assert current_segment_tagger_results == previous_segment_tagger_results

    # Make sure we have at least 5 fields (sanity check)
    assert len(current_fields_response) >= 5
