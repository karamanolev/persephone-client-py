import os

from persephone_client.client import PersephoneException, PersephoneClient


class PersephoneBuildHelper:
    """High-level helper to manage builds and upload screenshots in a stateful manner."""

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


class JenkinsBuildHelper(PersephoneBuildHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            root_endpoint=kwargs.pop('root_endpoint', os.getenv('PERSEPHONE_ENDPOINT')),
            username=kwargs.pop('username', os.getenv('PERSEPHONE_USERNAME')),
            password=kwargs.pop('password', os.getenv('PERSEPHONE_PASSWORD')),
            project_id=kwargs.pop('project_id', os.getenv('PERSEPHONE_PROJECT_ID')),
            commit_hash=kwargs.pop('commit_hash', os.getenv(
                'ghprbActualCommit', os.getenv('GIT_COMMIT'))),
            branch_name=kwargs.pop('branch_name', os.getenv(
                'ghprbSourceBranch', os.getenv('GIT_BRANCH'))),
            original_build_number=kwargs.pop('original_build_number', os.getenv('BUILD_NUMBER')),
            original_build_url=kwargs.pop('original_build_url', os.getenv('BUILD_URL')),
            pull_request_id=kwargs.pop('pull_request_id', os.getenv('ghprbPullId')),
            **kwargs,
        )


class CircleCIBuildHelper(PersephoneBuildHelper):
    def __init__(self, *args, **kwargs):
        env_pull_request_id = os.environ.get('CI_PULL_REQUEST', '').split('/')[-1]
        super().__init__(
            *args,
            root_endpoint=kwargs.pop('root_endpoint', os.getenv('PERSEPHONE_ENDPOINT')),
            username=kwargs.pop('username', os.getenv('PERSEPHONE_USERNAME')),
            password=kwargs.pop('password', os.getenv('PERSEPHONE_PASSWORD')),
            project_id=kwargs.pop('project_id', os.getenv('PERSEPHONE_PROJECT_ID')),
            commit_hash=kwargs.pop('commit_hash', os.getenv('CIRCLE_SHA1')),
            branch_name=kwargs.pop('branch_name', os.getenv('CIRCLE_BRANCH')),
            original_build_number=kwargs.pop(
                'original_build_number', os.getenv('CIRCLE_BUILD_NUM')),
            original_build_url=kwargs.pop('original_build_url', os.getenv('CIRCLE_BUILD_URL')),
            pull_request_id=kwargs.pop('pull_request_id', env_pull_request_id),
            **kwargs,
        )
