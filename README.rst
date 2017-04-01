====================
persephone-client-py
====================
A Python client for the Persephone REST API
-------------------------------------------

1. Installation
===============

You can install persephone-client-pi from pip::

    $ pip install persephone-client-py

2. Usage
========

There are two main classes - ``PersephoneClient`` and ``PersephoneBuildHelper``. The former can be
used to access the full-range of the API, while the latter is more useful during a CI run in order
to create a build, upload screenshots and finish the build.

3. Using ``PersephoneBuildHelper`` to submit screenshots during a build
=======================================================================

The example here uses the standard Jenkins environment variables. You can use anything else instead::

    # For example in your setUpClass method or wrapper script
    persephone = PersephoneBuildHelper(
        'http://persephone.yourdomain.com',
        'username',
        'password',
        '1',
        os.getenv('ghprbActualCommit'),
        os.getenv('ghprbSourceBranch'),
        os.getenv('BUILD_NUMBER'),
        os.getenv('BUILD_URL'),
        os.getenv('ghprbPullId'),
    )
    persephone.create_build()
    # In your testcase, assuming self.driver is a Selenium driver instance
    persephone.upload_screenshot('Main Page.png', self.driver.screenshot_as_png())
    # After the build is finished - tearDownClass or end of wrapper script
    persephone.finish_build()

If you create the build and then want to use a separate instance of ``PersephoneBuildHelper`` to
upload the screenshots (for example the build is managed by a wrapper script), you can access the
build ID using ``persephone.build_id`` right after calling ``create_build`` and pass that to the
testing module. Inside, you can create a minimal ``PersephoneBuildHelper`` using only the endpoint,
username, password and build_id and use that to upload the screenshots.

4. Using the command line interface
===================================

After you install persephone-client-py, you can use the ``persephone_cli`` command-line interface to
manage builds and upload screenshots. The configuration parameters (endpoint, username, etc.) can be
passed via environment variables or command line options. You can list the options using
``persephone_cli --help``. The environment variables are available with the ``PERSEPHONE_`` prefix.
For example, if the command-line option is ``--commit-hash`` the respective environment variable is
``PERSEPHONE_COMMIT_HASH``. The environment variables, if present, can still be overridden using the
command line options.

Creating a build::

    $ persephone-cli --endpoint "http://persephone.yourdomain.com/" --username admin \
        --password admin create_build
    5

The above command outputs the new build ID. To upload a screenshot::

    $ persephone-cli --endpoint "http://persephone.yourdomain.com/" --username admin \
        --password admin upload_screenshot --build-id 5 --image-path myimage.png \
        --image-name "Main Page.png"
