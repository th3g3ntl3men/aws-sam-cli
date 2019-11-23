"""
Tests whether SAM Config is being read by all CLI commands
"""

import json
import os
import shutil
import tempfile
from pathlib import Path
from contextlib import contextmanager
from samcli.lib.config.samconfig import SamConfig, DEFAULT_ENV

from click.testing import CliRunner

from unittest import TestCase
from unittest.mock import patch, ANY
import logging

LOG = logging.getLogger()
logging.basicConfig()


class TestSamConfigForAllCommands(TestCase):
    def setUp(self):
        self._old_cwd = os.getcwd()

        self.scratch_dir = tempfile.mkdtemp()
        Path(self.scratch_dir, "envvar.json").write_text("{}")

        os.chdir(self.scratch_dir)

    def tearDown(self):
        os.chdir(self._old_cwd)
        shutil.rmtree(self.scratch_dir)
        self.scratch_dir = None

    @patch("samcli.commands.init.do_cli")
    def test_init(self, do_cli_mock):
        config_values = {
            "no_interactive": True,
            "location": "github.com",
            "runtime": "nodejs10.x",
            "dependency_manager": "maven",
            "output_dir": "myoutput",
            "name": "myname",
            "app_template": "apptemplate",
            "no_input": True,
            "extra_context": '{"key": "value", "key2": "value2"}',
        }

        with samconfig_parameters(["init"], self.scratch_dir, **config_values) as config_path:
            from samcli.commands.init import cli

            LOG.debug(Path(config_path).read_text())
            runner = CliRunner()
            result = runner.invoke(cli, [])

            LOG.info(result.output)
            LOG.info(result.exception)
            if result.exception:
                LOG.exception("Command failed", exc_info=result.exc_info)
            self.assertIsNone(result.exception)

            do_cli_mock.assert_called_with(
                ANY,
                True,
                "github.com",
                "nodejs10.x",
                "maven",
                "myoutput",
                "myname",
                "apptemplate",
                True,
                '{"key": "value", "key2": "value2"}',
            )

    @patch("samcli.commands.validate.validate.do_cli")
    def test_validate(self, do_cli_mock):
        config_values = {"template_file": "mytemplate.yaml"}

        with samconfig_parameters(["validate"], self.scratch_dir, **config_values) as config_path:

            from samcli.commands.validate.validate import cli

            LOG.debug(Path(config_path).read_text())
            runner = CliRunner()
            result = runner.invoke(cli, [])

            LOG.info(result.output)
            LOG.info(result.exception)
            if result.exception:
                LOG.exception("Command failed", exc_info=result.exc_info)
            self.assertIsNone(result.exception)

            do_cli_mock.assert_called_with(ANY, str(Path(os.getcwd(), "mytemplate.yaml")))

    @patch("samcli.commands.build.command.do_cli")
    def test_build(self, do_cli_mock):
        config_values = {
            "function_identifier": "foo",
            "template_file": "mytemplate.yaml",
            "base_dir": "basedir",
            "build_dir": "builddir",
            "use_container": True,
            "manifest": "requirements.txt",
            "docker_network": "mynetwork",
            "skip_pull_image": True,
            "parameter_overrides": "ParameterKey=Key,ParameterValue=Value ParameterKey=Key2,ParameterValue=Value2",
        }

        with samconfig_parameters(["build"], self.scratch_dir, **config_values) as config_path:

            from samcli.commands.build.command import cli

            LOG.debug(Path(config_path).read_text())
            runner = CliRunner()
            result = runner.invoke(cli, [])

            LOG.info(result.output)
            LOG.info(result.exception)
            if result.exception:
                LOG.exception("Command failed", exc_info=result.exc_info)
            self.assertIsNone(result.exception)

            do_cli_mock.assert_called_with(
                "foo",
                str(Path(os.getcwd(), "mytemplate.yaml")),
                "basedir",
                "builddir",
                True,
                True,
                "requirements.txt",
                "mynetwork",
                True,
                {"Key": "Value", "Key2": "Value2"},
                None,
            )

    @patch("samcli.commands.local.invoke.cli.do_cli")
    def test_local_invoke(self, do_cli_mock):
        config_values = {
            "function_identifier": "foo",
            "template_file": "mytemplate.yaml",
            "event": "event",
            "no_event": False,
            "env_vars": "envvar.json",
            "debug_port": [1, 2, 3],
            "debug_args": "args",
            "debugger_path": "mypath",
            "docker_volume_basedir": "basedir",
            "docker_network": "mynetwork",
            "log_file": "logfile",
            "layer_cache_basedir": "basedir",
            "skip_pull_image": True,
            "force_image_build": True,
            "parameter_overrides": "ParameterKey=Key,ParameterValue=Value ParameterKey=Key2,ParameterValue=Value2",
        }

        # NOTE: Because we don't load the full Click BaseCommand here, this is mounted as top-level command
        with samconfig_parameters(["invoke"], self.scratch_dir, **config_values) as config_path:

            from samcli.commands.local.invoke.cli import cli

            LOG.debug(Path(config_path).read_text())
            runner = CliRunner()
            result = runner.invoke(cli, [])

            LOG.info(result.output)
            LOG.info(result.exception)
            if result.exception:
                LOG.exception("Command failed", exc_info=result.exc_info)
            self.assertIsNone(result.exception)

            do_cli_mock.assert_called_with(
                ANY,
                "foo",
                str(Path(os.getcwd(), "mytemplate.yaml")),
                "event",
                False,
                "envvar.json",
                (1, 2, 3),
                "args",
                "mypath",
                "basedir",
                "mynetwork",
                "logfile",
                "basedir",
                True,
                True,
                {"Key": "Value", "Key2": "Value2"},
            )

    @patch("samcli.commands.local.start_api.cli.do_cli")
    def test_local_start_api(self, do_cli_mock):

        config_values = {
            "template_file": "mytemplate.yaml",
            "host": "127.0.0.1",
            "port": 12345,
            "static_dir": "static_dir",
            "env_vars": "envvar.json",
            "debug_port": [1, 2, 3],
            "debug_args": "args",
            "debugger_path": "mypath",
            "docker_volume_basedir": "basedir",
            "docker_network": "mynetwork",
            "log_file": "logfile",
            "layer_cache_basedir": "basedir",
            "skip_pull_image": True,
            "force_image_build": True,
            "parameter_overrides": "ParameterKey=Key,ParameterValue=Value ParameterKey=Key2,ParameterValue=Value2",
        }

        # NOTE: Because we don't load the full Click BaseCommand here, this is mounted as top-level command
        with samconfig_parameters(["start-api"], self.scratch_dir, **config_values) as config_path:

            from samcli.commands.local.start_api.cli import cli

            LOG.debug(Path(config_path).read_text())
            runner = CliRunner()
            result = runner.invoke(cli, [])

            LOG.info(result.output)
            LOG.info(result.exception)
            if result.exception:
                LOG.exception("Command failed", exc_info=result.exc_info)
            self.assertIsNone(result.exception)

            do_cli_mock.assert_called_with(
                ANY,
                "127.0.0.1",
                12345,
                "static_dir",
                str(Path(os.getcwd(), "mytemplate.yaml")),
                "envvar.json",
                (1, 2, 3),
                "args",
                "mypath",
                "basedir",
                "mynetwork",
                "logfile",
                "basedir",
                True,
                True,
                {"Key": "Value", "Key2": "Value2"},
            )

    @patch("samcli.commands.local.start_lambda.cli.do_cli")
    def test_local_start_lambda(self, do_cli_mock):

        config_values = {
            "template_file": "mytemplate.yaml",
            "host": "127.0.0.1",
            "port": 12345,
            "env_vars": "envvar.json",
            "debug_port": [1, 2, 3],
            "debug_args": "args",
            "debugger_path": "mypath",
            "docker_volume_basedir": "basedir",
            "docker_network": "mynetwork",
            "log_file": "logfile",
            "layer_cache_basedir": "basedir",
            "skip_pull_image": True,
            "force_image_build": True,
            "parameter_overrides": "ParameterKey=Key,ParameterValue=Value",
        }

        # NOTE: Because we don't load the full Click BaseCommand here, this is mounted as top-level command
        with samconfig_parameters(["start-lambda"], self.scratch_dir, **config_values) as config_path:

            from samcli.commands.local.start_lambda.cli import cli

            LOG.debug(Path(config_path).read_text())
            runner = CliRunner()
            result = runner.invoke(cli, [])

            LOG.info(result.output)
            LOG.info(result.exception)
            if result.exception:
                LOG.exception("Command failed", exc_info=result.exc_info)
            self.assertIsNone(result.exception)

            do_cli_mock.assert_called_with(
                ANY,
                "127.0.0.1",
                12345,
                str(Path(os.getcwd(), "mytemplate.yaml")),
                "envvar.json",
                (1, 2, 3),
                "args",
                "mypath",
                "basedir",
                "mynetwork",
                "logfile",
                "basedir",
                True,
                True,
                {"Key": "Value"},
            )

    @patch("samcli.commands.package.command.do_cli")
    def test_package(self, do_cli_mock):

        config_values = {
            "template_file": "mytemplate.yaml",
            "s3_bucket": "mybucket",
            "force_upload": True,
            "s3_prefix": "myprefix",
            "kms_key_id": "mykms",
            "use_json": True,
            "metadata": '{"m1": "value1", "m2": "value2"}',
            "region": "myregion",
            "output_template_file": "output.yaml",
        }

        with samconfig_parameters(["package"], self.scratch_dir, **config_values) as config_path:

            from samcli.commands.package.command import cli

            LOG.debug(Path(config_path).read_text())
            runner = CliRunner()
            result = runner.invoke(cli, [])

            LOG.info(result.output)
            LOG.info(result.exception)
            if result.exception:
                LOG.exception("Command failed", exc_info=result.exc_info)
            self.assertIsNone(result.exception)

            do_cli_mock.assert_called_with(
                str(Path(os.getcwd(), "mytemplate.yaml")),
                "mybucket",
                "myprefix",
                "mykms",
                "output.yaml",
                True,
                True,
                {"m1": "value1", "m2": "value2"},
                "myregion",
                None,
            )

    @patch("samcli.commands.deploy.command.do_cli")
    def test_deploy(self, do_cli_mock):

        config_values = {
            "template_file": "mytemplate.yaml",
            "stack_name": "mystack",
            "s3_bucket": "mybucket",
            "force_upload": True,
            "s3_prefix": "myprefix",
            "kms_key_id": "mykms",
            "parameter_overrides": "ParameterKey=Key,ParameterValue=Value",
            "capabilities": "cap1 cap2",
            "no_execute_changeset": True,
            "role_arn": "arn",
            "notification_arns": "notify1 notify2",
            "fail_on_empty_changeset": True,
            "use_json": True,
            "tags": 'a=tag1 b="tag with spaces"',
            "metadata": '{"m1": "value1", "m2": "value2"}',
            "guided": True,
            "confirm_changeset": True,
            "region": "myregion",
        }

        with samconfig_parameters(["deploy"], self.scratch_dir, **config_values) as config_path:

            from samcli.commands.deploy.command import cli

            LOG.debug(Path(config_path).read_text())
            runner = CliRunner()
            result = runner.invoke(cli, [])

            LOG.info(result.output)
            LOG.info(result.exception)
            if result.exception:
                LOG.exception("Command failed", exc_info=result.exc_info)
            self.assertIsNone(result.exception)

            do_cli_mock.assert_called_with(
                str(Path(os.getcwd(), "mytemplate.yaml")),
                "mystack",
                "mybucket",
                True,
                "myprefix",
                "mykms",
                {"Key": "Value"},
                ["cap1", "cap2"],
                True,
                "arn",
                ["notify1", "notify2"],
                True,
                True,
                {"a": "tag1", "b": '"tag with spaces"'},
                {"m1": "value1", "m2": "value2"},
                True,
                True,
                "myregion",
                None,
            )

    @patch("samcli.commands.logs.command.do_cli")
    def test_logs(self, do_cli_mock):
        config_values = {
            "name": "myfunction",
            "stack_name": "mystack",
            "filter": "myfilter",
            "tail": True,
            "start_time": "starttime",
            "end_time": "endtime",
        }

        with samconfig_parameters(["logs"], self.scratch_dir, **config_values) as config_path:
            from samcli.commands.logs.command import cli

            LOG.debug(Path(config_path).read_text())
            runner = CliRunner()
            result = runner.invoke(cli, [])

            LOG.info(result.output)
            LOG.info(result.exception)
            if result.exception:
                LOG.exception("Command failed", exc_info=result.exc_info)
            self.assertIsNone(result.exception)

            do_cli_mock.assert_called_with("myfunction", "mystack", "myfilter", True, "starttime", "endtime")

    @patch("samcli.commands.publish.command.do_cli")
    def test_publish(self, do_cli_mock):
        config_values = {"template_file": "mytemplate.yaml", "semantic_version": "0.1.1"}

        with samconfig_parameters(["publish"], self.scratch_dir, **config_values) as config_path:
            from samcli.commands.publish.command import cli

            LOG.debug(Path(config_path).read_text())
            runner = CliRunner()
            result = runner.invoke(cli, [])

            LOG.info(result.output)
            LOG.info(result.exception)
            if result.exception:
                LOG.exception("Command failed", exc_info=result.exc_info)
            self.assertIsNone(result.exception)

            do_cli_mock.assert_called_with(ANY, str(Path(os.getcwd(), "mytemplate.yaml")), "0.1.1")

    def test_info_must_not_read_from_config(self):
        config_values = {"a": "b"}

        with samconfig_parameters([], self.scratch_dir, **config_values) as config_path:
            from samcli.cli.main import cli

            LOG.debug(Path(config_path).read_text())
            runner = CliRunner()
            result = runner.invoke(cli, ["--info"])

            LOG.info(result.exception)
            if result.exception:
                LOG.exception("Command failed", exc_info=result.exc_info)
            self.assertIsNone(result.exception)

            info_result = json.loads(result.output)
            self.assertTrue("version" in info_result)


class TestSamConfigWithOverrides(TestCase):
    def setUp(self):
        self._old_cwd = os.getcwd()

        self.scratch_dir = tempfile.mkdtemp()
        Path(self.scratch_dir, "otherenvvar.json").write_text("{}")

        os.chdir(self.scratch_dir)

    def tearDown(self):
        os.chdir(self._old_cwd)
        shutil.rmtree(self.scratch_dir)
        self.scratch_dir = None

    @patch("samcli.commands.local.start_lambda.cli.do_cli")
    def test_override_with_cli_params(self, do_cli_mock):

        config_values = {
            "template_file": "mytemplate.yaml",
            "host": "127.0.0.1",
            "port": 12345,
            "env_vars": "envvar.json",
            "debug_port": [1, 2, 3],
            "debug_args": "args",
            "debugger_path": "mypath",
            "docker_volume_basedir": "basedir",
            "docker_network": "mynetwork",
            "log_file": "logfile",
            "layer_cache_basedir": "basedir",
            "skip_pull_image": True,
            "force_image_build": True,
            "parameter_overrides": "ParameterKey=Key,ParameterValue=Value",
        }

        # NOTE: Because we don't load the full Click BaseCommand here, this is mounted as top-level command
        with samconfig_parameters(["start-lambda"], self.scratch_dir, **config_values) as config_path:

            from samcli.commands.local.start_lambda.cli import cli

            LOG.debug(Path(config_path).read_text())
            runner = CliRunner()
            result = runner.invoke(
                cli,
                [
                    "--template-file",
                    "othertemplate.yaml",
                    "--host",
                    "otherhost",
                    "--port",
                    9999,
                    "--env-vars",
                    "otherenvvar.json",
                    "--debug-port",
                    9,
                    "--debug-port",
                    8,
                    "--debug-port",
                    7,
                    "--debug-args",
                    "otherargs",
                    "--debugger-path",
                    "otherpath",
                    "--docker-volume-basedir",
                    "otherbasedir",
                    "--docker-network",
                    "othernetwork",
                    "--log-file",
                    "otherlogfile",
                    "--layer-cache-basedir",
                    "otherbasedir",
                    "--skip-pull-image",
                    "--force-image-build",
                    "--parameter-overrides",
                    "A=123 C=D E=F12! G=H",
                ],
            )

            LOG.info(result.output)
            LOG.info(result.exception)
            if result.exception:
                LOG.exception("Command failed", exc_info=result.exc_info)
            self.assertIsNone(result.exception)

            do_cli_mock.assert_called_with(
                ANY,
                "otherhost",
                9999,
                str(Path(os.getcwd(), "othertemplate.yaml")),
                "otherenvvar.json",
                (9, 8, 7),
                "otherargs",
                "otherpath",
                "otherbasedir",
                "othernetwork",
                "otherlogfile",
                "otherbasedir",
                True,
                True,
                {"A": "123", "C": "D", "E": "F12!", "G": "H"},
            )

    @patch("samcli.commands.local.start_lambda.cli.do_cli")
    def test_override_with_cli_params_and_envvars(self, do_cli_mock):

        config_values = {
            "template_file": "mytemplate.yaml",
            "host": "127.0.0.1",
            "port": 12345,
            "env_vars": "envvar.json",
            "debug_port": [1, 2, 3],
            "debug_args": "args",
            "debugger_path": "mypath",
            "docker_volume_basedir": "basedir",
            "docker_network": "mynetwork",
            "log_file": "logfile",
            "layer_cache_basedir": "basedir",
            "skip_pull_image": True,
            "force_image_build": False,
        }

        # NOTE: Because we don't load the full Click BaseCommand here, this is mounted as top-level command
        with samconfig_parameters(["start-lambda"], self.scratch_dir, **config_values) as config_path:

            from samcli.commands.local.start_lambda.cli import cli

            LOG.debug(Path(config_path).read_text())
            runner = CliRunner()
            result = runner.invoke(
                cli,
                env={
                    "SAM_TEMPLATE_FILE": "envtemplate.yaml",
                    "SAM_SKIP_PULL_IMAGE": "False",
                    "SAM_FORCE_IMAGE_BUILD": "False",
                    "SAM_DOCKER_NETWORK": "envnetwork",
                    # Debug port is exclusively provided through envvars and not thru CLI args
                    "SAM_DEBUG_PORT": "13579",
                    "DEBUGGER_ARGS": "envargs",
                    "SAM_DOCKER_VOLUME_BASEDIR": "envbasedir",
                    "SAM_LAYER_CACHE_BASEDIR": "envlayercache",
                },
                args=[
                    "--host",
                    "otherhost",
                    "--port",
                    9999,
                    "--env-vars",
                    "otherenvvar.json",
                    "--debugger-path",
                    "otherpath",
                    "--log-file",
                    "otherlogfile",
                    # this is a case where cli args takes precedence over both
                    # config file and envvar
                    "--force-image-build",
                    # Parameter overrides is exclusively provided through CLI args and not config
                    "--parameter-overrides",
                    "A=123 C=D E=F12! G=H",
                ],
            )

            LOG.info(result.output)
            LOG.info(result.exception)
            if result.exception:
                LOG.exception("Command failed", exc_info=result.exc_info)
            self.assertIsNone(result.exception)

            do_cli_mock.assert_called_with(
                ANY,
                "otherhost",
                9999,
                str(Path(os.getcwd(), "envtemplate.yaml")),
                "otherenvvar.json",
                (13579,),
                "envargs",
                "otherpath",
                "envbasedir",
                "envnetwork",
                "otherlogfile",
                "envlayercache",
                False,
                True,
                {"A": "123", "C": "D", "E": "F12!", "G": "H"},
            )


@contextmanager
def samconfig_parameters(cmd_names, config_dir=None, env=None, **kwargs):
    """
    ContextManager to write a new SAM Config and remove the file after the contextmanager exists

    Parameters
    ----------
    cmd_names : list(str)
        Name of the full commnad split as a list: ["generate-event", "s3", "put"]

    config_dir : str
        Path where the SAM config file should be written to. Defaults to os.getcwd()

    env : str
        Optional name of the config environment. This is currently unused

    kwargs : dict
        Parameter names and values to be written to the file.

    Returns
    -------
    Path to the config file
    """

    env = env or DEFAULT_ENV
    section = "parameters"
    samconfig = SamConfig(config_dir=config_dir)

    try:
        for k, v in kwargs.items():
            samconfig.put(cmd_names, section, k, v, env=env)

        samconfig.flush()
        yield samconfig.path()
    finally:
        Path(samconfig.path()).unlink()