# -*- coding: utf-8 -*-
"""
    test_actions.py
    :copyright: © 2019 by the EAB Tech team.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
        http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""


import json
from juniper import actions
from unittest.mock import MagicMock
from juniper.io import (reader, get_artifact_path)

logger = MagicMock()


def test_build_compose_sections():
    """
    Using the processor-test as a sample definition of the lambda functions to
    be packaged. Make sure that the resources portion of the file is correctly
    generated.

    The sections portion of the file, takes into account the volume mappings
    as well as well as the command to invoke when docker-compose is invoked.
    """

    processor_ctx = reader('./tests/processor-test.yml')
    result = actions._get_compose_sections(processor_ctx)

    # The fully converted docker-compose.yml file as created by the action.
    expected = read_expectation('./tests/expectations/processor-sections.yml')

    assert result == expected


def test_build_compose_writes_compose_definition_to_tmp_file(mocker):
    """
    The docker-compose file created, is written to a tmp file. Make sure that
    the file is writen and validate that the contents of the file match the
    expected result.
    """

    tmp_filename = '/var/folders/xw/yk2rrhks1w72y0zr_7t7b851qlt8b3/T/tmp52bd77s3'
    mock_writer = mocker.patch('juniper.actions.write_tmp_file', return_value=tmp_filename)

    processor_ctx = reader('./tests/processor-test.yml')
    actual_filename = actions.build_compose(logger, processor_ctx)

    expected = read_expectation('./tests/expectations/processor-compose.yml')

    assert tmp_filename == actual_filename
    assert mock_writer.call_args[0][0] == expected


def test_build_artifacts_invokes_docker_commands(mocker):
    """
    Validate that the docker-compose commands are executed with the valid paramters.
    Since the docker-compose file was dynamically generated, we must pass the full
    path of that file to docker-compose command. Also, set the context of the execution
    to the current path.
    """

    tmp_filename = '/var/folders/xw/yk2rrhks1w72y0zr_7t7b851qlt8b3/T/tmp52bd77s3'
    mock_builder = mocker.patch('juniper.actions.build_compose', return_value=tmp_filename)

    # Mocking the dependencies of this action. These three high level packages are
    # needed to invoke docker-compose in the right context!
    mocker.patch('juniper.actions.os')
    mocker.patch('juniper.actions.shutil')
    mock_subprocess_run = mocker.patch('juniper.actions.subprocess.run')

    compose_cmd_calls = [
        mocker.call(["docker-compose", "-f", tmp_filename, '--project-directory', '.', 'down']),
        mocker.call(["docker-compose", "-f", tmp_filename, '--project-directory', '.', 'up'])
    ]

    processor_ctx = reader('./tests/processor-test.yml')
    actions.build_artifacts(logger, processor_ctx)

    mock_subprocess_run.assert_has_calls(compose_cmd_calls)
    mock_builder.assert_called_once()


def test_build_artifacts_copies_scriopts(mocker):
    """
    Since the docker-compose command will be executed from within the context
    of where the lambda functions live. We need to make sure that the `package.sh`
    lives in the right context.

    Validate that a bin folder is temporarily created in the folder of the caller.
    This folder will be removed after the .zip artifacts are generated.
    """

    tmp_filename = '/var/folders/xw/yk2rrhks1w72y0zr_7t7b851qlt8b3/T/tmp52bd77s3'
    mock_builder = mocker.patch('juniper.actions.build_compose', return_value=tmp_filename)

    # Mocking the dependencies of this action. These three high level packages are
    # needed to invoke docker-compose in the right context!
    mock_os = mocker.patch('juniper.actions.os')
    mock_shutil = mocker.patch('juniper.actions.shutil')
    mocker.patch('juniper.actions.subprocess.run')

    processor_ctx = reader('./tests/processor-test.yml')
    actions.build_artifacts(logger, processor_ctx)

    # Validate that this three step process is correctly executed.
    mock_os.makedirs.assert_called_with('./.juni/bin', exist_ok=True)
    mock_shutil.copy.assert_called_with(get_artifact_path('package.sh'), './.juni/bin/')
    mock_shutil.rmtree.assert_called_with('./.juni', ignore_errors=True)
    mock_builder.assert_called_once()


def test_build_compose_section_custom_output():
    """
    Validate that given a custom output directory, the volume mapping incldues
    the custom value instead of the default dist.
    """

    sls_function = {}
    custom_output_dir = './build_not_dist'
    template = '"function_name": "{name}", "volumes": "{volumes}"'
    context = {'package': {'output': custom_output_dir}}

    result = actions._build_compose_section(context, template, 'test_func', sls_function)
    as_json = json.loads('{' + result.replace('\n', '\\n') + '}')

    assert len([
        volume.strip()
        for volume in as_json['volumes'].split('\n')
        if custom_output_dir in volume
    ])


def read_expectation(file_name):

    with open(file_name, 'r') as f:
        return f.read()
