import json
from urllib import parse

import requests


class PersephoneException(Exception):
    pass


class PersephoneClient:
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


class PersephoneBuildHelper:
    def __init__(self,
                 root_endpoint,
                 username,
                 password,
                 project_id,
                 commit_hash=None,
                 branch_name=None,
                 original_build_number=None,
                 original_build_url=None,
                 pull_request_id=None,
                 build_id=None,
                 ):
        """
        Creates an instance of the PersephoneClient
        :param root_endpoint: The public endpoint where your Persephone is accessible, for example
        http://persephone.yourdomain.com/. The REST API should be accessible under /api/v1/ of
        that URL.
        :param project_id: The Persephone project ID where screenshots will be uploaded.
        :param username: The username for a Persephone account
        :param password: The password foa a Persephone account
        :param commit_hash: The hash of the commit which is being built. (required)
        :param branch_name: The branch name that is being built. Master has spacial handling
        throughout the project. (optional)
        :param original_build_number: The build number in your CI environment, mainly for tracking
        purposes. (optional)
        :param original_build_url: The absolute URL for the build page in your CI environment,
        mainly for tracking purposes. (optional)
        :param pull_request_id: The pull request ID in GitHub for this build. (optional)
        :param build_id: The Persephone build ID. Important: only specify this if the build is
        already created in another process and you only want to upload screenshots.
        """
        self.client = PersephoneClient(root_endpoint, username, password)
        self.project_id = project_id
        self.commit_hash = commit_hash
        self.branch_name = branch_name
        self.original_build_number = original_build_number
        self.original_build_url = original_build_url
        self.pull_request_id = pull_request_id
        self.build_id = build_id

    def create_build(self):
        """
        Creates a build in Persephone and saves the build id in self.build_id
        """
        if self.build_id:
            raise PersephoneException(
                'There is already a build running. '
                'Please finish or fail the previous one before creating a new one.')
        build = self.client.create_build(
            self.project_id,
            self.commit_hash,
            self.branch_name,
            self.original_build_number,
            self.original_build_url,
            self.pull_request_id,
        )
        self.build_id = build['id']

    def delete_build(self):
        """
        Deletes the current build.
        """
        if not self.build_id:
            raise PersephoneException('No build is running. Please create a build first.')
        self.client.delete_build(self.project_id, self.build_id)
        self.build_id = None

    def finish_build(self):
        """Marks the current build as finished."""
        if not self.build_id:
            raise PersephoneException('No build is running. Please create a build first.')
        self.client.finish_build(self.project_id, self.build_id)
        self.build_id = None

    def fail_build(self):
        """Marks the current build as failed."""
        if not self.build_id:
            raise PersephoneException('No build is running. Please create a build first.')
        self.client.fail_build(self.project_id, self.build_id)
        self.build_id = None

    def upload_screenshot(self, name, image_data, metadata=None):
        """
        Uploads a screenshot to the current build.
        :param name: A freeform name for the screenshot (e.g. subfolder/image.png).
        :param image_data: A bytes object with a PNG screenshot.
        :param metadata: An optional freeform dict with JSON serializable values to attach to the
        image as metadata.
        """
        if not self.build_id:
            raise PersephoneException('No build is running. Please create a build first.')
        screenshot = self.client.post_screenshot(
            self.project_id, self.build_id, name, image_data, metadata)
        return screenshot['id']
