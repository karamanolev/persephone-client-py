#!/usr/bin/env python

import argparse
import json
import os
import sys

from persephone_client import PersephoneBuildHelper


def main():
    root_endpoint = os.getenv('PERSEPHONE_ENDPOINT')
    username = os.getenv('PERSEPHONE_USERNAME')
    password = os.getenv('PERSEPHONE_PASSWORD')
    project_id = os.getenv('PERSEPHONE_PROJECT_ID')
    commit_hash = os.getenv('PERSEPHONE_COMMIT_HASH')
    branch_name = os.getenv('PERSEPHONE_BRANCH_NAME')
    original_build_number = os.getenv('PERSEPHONE_ORIGINAL_BUILD_NUMBER')
    original_build_url = os.getenv('PERSEPHONE_ORIGINAL_BUILD_URL')
    pull_request_id = os.getenv('PERSEPHONE_PULL_REQUEST_ID')
    build_id = os.getenv('PERSEPHONE_BUILD_ID')

    parser = argparse.ArgumentParser(prog='persephone_cli')
    parser.add_argument('--endpoint', default=root_endpoint, required=not root_endpoint)
    parser.add_argument('--username', default=username, required=not username)
    parser.add_argument('--password', default=password, required=not password)
    parser.add_argument('--project-id', default=project_id, required=not project_id)
    parser.add_argument('--commit-hash', default=commit_hash, required=False)
    parser.add_argument('--branch-name', default=branch_name, required=False)
    parser.add_argument('--original-build-number', default=original_build_number, required=False)
    parser.add_argument('--original-build-url', default=original_build_url, required=False)
    parser.add_argument('--pull-request-id', default=pull_request_id, required=False)
    subparsers = parser.add_subparsers()

    parser_create_build = subparsers.add_parser('create-build')
    parser_create_build.set_defaults(action='create-build')

    parser_delete_build = subparsers.add_parser('delete_build')
    parser_delete_build.set_defaults(action='delete_build')
    parser_delete_build.add_argument('--build-id', default=build_id, required=False)

    parser_finish_build = subparsers.add_parser('finish_build')
    parser_finish_build.set_defaults(action='finish_build')
    parser_finish_build.add_argument('--build-id', default=build_id, required=False)

    parser_fail_build = subparsers.add_parser('fail_build')
    parser_fail_build.set_defaults(action='fail_build')
    parser_fail_build.add_argument('--build-id', default=build_id, required=False)

    parser_upload_screenshot = subparsers.add_parser('upload_screenshot')
    parser_upload_screenshot.set_defaults(action='upload_screenshot')
    parser_upload_screenshot.add_argument('--build-id', default=build_id, required=False)
    parser_upload_screenshot.add_argument('--image-path', default=None)
    parser_upload_screenshot.add_argument('--image-name', default=None)
    parser_upload_screenshot.add_argument('--image-metadata', default=None)

    args = parser.parse_args()

    root_endpoint = args.endpoint
    username = args.username
    password = args.password
    project_id = args.project_id
    commit_hash = args.commit_hash
    branch_name = args.branch_name
    original_build_number = args.original_build_number
    original_build_url = args.original_build_url
    pull_request_id = args.pull_request_id
    build_id = args.build_id

    image_path = args.image_path
    image_name = args.image_name
    image_metadata = args.image_metadata

    action = args.action

    client = PersephoneBuildHelper(
        root_endpoint,
        username,
        password,
        project_id,
        commit_hash,
        branch_name,
        original_build_number,
        original_build_url,
        pull_request_id,
        build_id,
    )

    if action == 'create-build':
        build = client.create_build()
        print(build['id'])
    elif action == 'delete-build':
        if not build_id:
            print('ERROR: Please specify a build id.')
            sys.exit(1)
        client.delete_build()
    elif action == 'finish-build':
        if not build_id:
            print('ERROR: Please specify a build id.')
            sys.exit(1)
        client.finish_build()
    elif action == 'fail-build':
        if not build_id:
            print('ERROR: Please specify a build id.')
            sys.exit(
                1)
        client.fail_build()
    elif action == 'fail-build':
        if not build_id:
            print('ERROR: Please specify a build id.')
            sys.exit(1)
        client.fail_build()
    elif action == 'upload-screenshot':
        if not build_id or not image_name or not image_path:
            print('ERROR: Please specify a build id, image name and image path.')
            sys.exit(1)
        with open(image_path, 'rb') as f:
            data = f.read()
        try:
            metadata = json.loads(image_metadata)
        except json.JSONDecodeError:
            print('ERROR: Image metadata must be a valid JSON.')
            sys.exit(1)
        screenshot_id = client.upload_screenshot(
            image_name,
            data,
            metadata,
        )
        print(screenshot_id)


if __name__ == '__main__':
    main()
