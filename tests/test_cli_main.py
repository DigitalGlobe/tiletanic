from click.testing import CliRunner

from tiletanic import cli

def test_tiletanic():
    """Basic call to root command"""
    runner = CliRunner()
    result = runner.invoke(cli.cli)
    assert result.exit_code == 0

def test_version():
    runner = CliRunner()
    result = runner.invoke(cli.cli, ['--version'])
    assert result.exit_code == 0
