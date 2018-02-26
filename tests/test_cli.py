import pytest
from click.testing import CliRunner
from hibernate_rebinder import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli(runner):
    result = runner.invoke(cli.main)
    assert result.exit_code == 2
    assert result.exception


def test_cli_with_arg(runner):
    with runner.isolated_filesystem():
        with open('example.txt', 'w') as f:
            f.write('insert into sample_table (pk_id, created, deployed, deployed_time, foreign_key, score, active) '
                    'values (?, ?, ?, ?, ?, ?, ?)\n')
            f.write('binding parameter[1] as [BIGINT] - 1\n')
            f.write('binding parameter[2] as [TIMESTAMP] - 2018-02-22 17:47:59.718\n')
            f.write('binding parameter[3] as [BOOLEAN] - false\n')
            f.write('binding parameter[4] as [TIMESTAMP] - <null>\n')
            f.write('binding parameter[5] as [BIGINT] - 1\n')
            f.write('binding parameter[6] as [DOUBLE] - 1.0\n')
            f.write('binding parameter[7] as [BOOLEAN] - true\n')

        result = runner.invoke(cli.main, ['example.txt'])
        assert result.exit_code == 0
        assert result.output.strip() == 'insert into sample_table ' \
                                        '(pk_id, created, deployed, deployed_time, foreign_key, score, active) ' \
                                        'values ' \
                                        '(1, "2018-02-22 17:47:59.718", 0, NULL, 1, 1.0, 0)'
