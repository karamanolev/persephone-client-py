import json
from urllib import parse

import requests


class PersephoneException(Exception):
    pass


class PersephoneClient:
    """A lower level client for the Persephone REST API"""

    def __init__(self, root_endpoint, username, password):
        self.root_endpoint = root_endpoint
        self.username = username
        self.password = password
        self._auth = (username, password)

    def _get_api_endpoint(self):
        return parse.urljoin(self.root_endpoint, 'api/v1/')

    def _get_projects_endpoint(self):
        return parse.urljoin(self._get_api_endpoint(), 'projects/')

    def _get_project_endpoint(self, project_id):
        return parse.urljoin(self._get_projects_endpoint(), '{}/'.format(project_id))

    def _get_builds_endpoint(self, project_id):
        return parse.urljoin(self._get_project_endpoint(project_id), 'builds/')

    def _get_build_endpoint(self, project_id, build_id):
        return parse.urljoin(self._get_builds_endpoint(project_id), '{}/'.format(build_id))

    def _get_screenshots_endpoint(self, project_id, build_id):
        return parse.urljoin(self._get_build_endpoint(project_id, build_id), 'screenshots/')

    def get_projects(self):
        resp = requests.get(self._get_projects_endpoint(), auth=self._auth)
        resp.raise_for_status()
        return resp.json()

    def get_project(self, project_id):
        resp = requests.get(self._get_project_endpoint(project_id), auth=self._auth)
        resp.raise_for_status()
        return resp.json()

    def get_builds(self, project_id):
        resp = requests.get(self._get_builds_endpoint(project_id), auth=self._auth)
        resp.raise_for_status()
        return resp.json()

    def get_build(self, project_id, build_id):
        resp = requests.get(self._get_build_endpoint(project_id, build_id), auth=self._auth)
        resp.raise_for_status()
        return resp.json()

    def create_build(self, project_id, commit_hash=None, branch_name=None,
                     original_build_number=None, original_build_url=None, pull_request_id=None):
        resp = requests.post(
            self._get_builds_endpoint(project_id),
            auth=self._auth,
            json={
                'commit_hash': commit_hash,
                'branch_name': branch_name,
                'original_build_number': original_build_number,
                'original_build_url': original_build_url,
                'pull_request_id': pull_request_id,
            })
        resp.raise_for_status()
        return resp.json()

    def delete_build(self, project_id, build_id):
        resp = requests.delete(self._get_build_endpoint(project_id, build_id), auth=self._auth)
        resp.raise_for_status()

    def finish_build(self, project_id, build_id):
        resp = requests.post(
            parse.urljoin(self._get_build_endpoint(project_id, build_id), 'finish'),
            auth=self._auth,
        )
        resp.raise_for_status()
        return resp.json()

    def fail_build(self, project_id, build_id):
        resp = requests.post(
            parse.urljoin(self._get_build_endpoint(project_id, build_id), 'fail'),
            auth=self._auth,
        )
        resp.raise_for_status()
        return resp.json()

    def post_screenshot(self, project_id, build_id, name, image_data, metadata):
        resp = requests.post(
            self._get_screenshots_endpoint(project_id, build_id),
            auth=self._auth,
            data={
                'name': name,
                'metadata': json.dumps(metadata),
            },
            files={
                'image': image_data,
            },
        )
        resp.raise_for_status()
        return resp.json()
