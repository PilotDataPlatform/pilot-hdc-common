# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.


import pytest

from common import ProjectClient
from common import ProjectException
from common import ProjectNotFoundException
from tests.conftest import PROJECT_DATA
from tests.conftest import PROJECT_ID
from tests.conftest import PROJECT_URL


async def test_get_by_code_200(redis, mock_get_by_code):
    project_client = ProjectClient(PROJECT_URL, redis.url)
    project = await project_client.get(code=PROJECT_DATA['code'])
    assert project.name == PROJECT_DATA['name']
    data = await project.json()
    assert data['name'] == PROJECT_DATA['name']


async def test_get_by_id_200(redis, mock_get_by_id):
    project_client = ProjectClient(PROJECT_URL, redis.url)
    project = await project_client.get(id=PROJECT_ID)
    assert project.name == PROJECT_DATA['name']
    data = await project.json()
    assert data['name'] == PROJECT_DATA['name']


async def test_get_by_id_bad_redis_200(redis, mock_get_by_id):
    project_client = ProjectClient(PROJECT_URL, 'redis://fake:1234')
    project = await project_client.get(id=PROJECT_ID)
    assert project.name == PROJECT_DATA['name']
    data = await project.json()
    assert data['name'] == PROJECT_DATA['name']


async def test_get_by_id_404(redis, httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url=PROJECT_URL + '/v1/projects/notfound',
        json={},
        status_code=404,
    )
    project_client = ProjectClient(PROJECT_URL, redis.url)
    with pytest.raises(ProjectNotFoundException):
        await project_client.get(code='notfound')


async def test_get_by_id_500(redis, httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url=PROJECT_URL + '/v1/projects/error',
        json={},
        status_code=500,
    )
    project_client = ProjectClient(PROJECT_URL, redis.url)
    with pytest.raises(ProjectException):
        await project_client.get(code='error')


async def test_project_update_200(redis, mock_get_by_code, httpx_mock):
    update_data = PROJECT_DATA.copy()
    update_data['name'] = 'updated'
    project_id = update_data['id']
    httpx_mock.add_response(
        method='PATCH',
        url=PROJECT_URL + f'/v1/projects/{project_id}',
        json=update_data,
        status_code=200,
    )

    project_client = ProjectClient(PROJECT_URL, redis.url, enable_cache=False)
    project = await project_client.get(code=PROJECT_DATA['code'])
    assert project.name == PROJECT_DATA['name']
    await project.update(name='updated')
    assert project.name == 'updated'


async def test_project_update_500(redis, mock_get_by_code, httpx_mock):
    update_data = PROJECT_DATA.copy()
    update_data['name'] = 'updated'
    project_id = update_data['id']
    httpx_mock.add_response(
        method='PATCH',
        url=PROJECT_URL + f'/v1/projects/{project_id}',
        json={},
        status_code=500,
    )

    project_client = ProjectClient(PROJECT_URL, redis.url, enable_cache=False)
    project = await project_client.get(code=PROJECT_DATA['code'])
    assert project.name == PROJECT_DATA['name']
    with pytest.raises(ProjectException):
        await project.update(name='updated')


async def test_create_project_200(redis, httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url=PROJECT_URL + '/v1/projects/',
        json=PROJECT_DATA,
        status_code=200,
    )

    project_client = ProjectClient(PROJECT_URL, redis.url, enable_cache=False)
    project = await project_client.create(
        name=PROJECT_DATA['name'],
        code=PROJECT_DATA['code'],
        description=PROJECT_DATA['description'],
        tags=PROJECT_DATA['tags'],
        system_tags=PROJECT_DATA['system_tags'],
    )
    assert project.name == PROJECT_DATA['name']


async def test_create_project_500(redis, httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url=PROJECT_URL + '/v1/projects/',
        json={},
        status_code=500,
    )

    project_client = ProjectClient(PROJECT_URL, redis.url, enable_cache=False)
    with pytest.raises(ProjectException):
        await project_client.create(
            name=PROJECT_DATA['name'],
            code=PROJECT_DATA['code'],
            description=PROJECT_DATA['description'],
            tags=PROJECT_DATA['tags'],
            system_tags=PROJECT_DATA['system_tags'],
        )


async def test_project_search_200(redis, httpx_mock):
    result = {
        'result': [PROJECT_DATA],
        'total': 1,
    }
    url = PROJECT_URL + (
        '/v1/projects/?name=Unit+Test+Project&code=unittestproject&description=Test' '&tags_all=tag1&tags_all=tag2'
    )
    httpx_mock.add_response(
        method='GET',
        url=url,
        json=result,
        status_code=200,
    )

    project_client = ProjectClient(PROJECT_URL, redis.url, enable_cache=False)
    result = await project_client.search(
        name=PROJECT_DATA['name'],
        code=PROJECT_DATA['code'],
        description=PROJECT_DATA['description'],
        tags_all=PROJECT_DATA['tags'],
    )
    assert result['result'][0].name == PROJECT_DATA['name']
    assert result['total'] == 1
