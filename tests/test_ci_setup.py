import os
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def setup_environment(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    scripts = {
        "python3": """#!/bin/bash
set -eu
printf 'venv %s\\n' "$*" >> "$SETUP_LOG"
if [[ "${FAIL_VENV:-}" == "1" ]]; then
    exit 7
fi
mkdir -p "$3/bin"
cp "$FAKE_BIN/python" "$3/bin/python"
cp "$FAKE_BIN/poetry" "$3/bin/poetry"
""",
        "python": """#!/bin/bash
printf 'python %s\\n' "$*" >> "$SETUP_LOG"
""",
        "poetry": """#!/bin/bash
printf 'poetry %s\\n' "$*" >> "$SETUP_LOG"
""",
    }
    for name, source in scripts.items():
        path = bin_dir / name
        path.write_text(source)
        path.chmod(0o755)
    env = os.environ.copy()
    env.pop("POETRY_HOME", None)
    env.pop("POETRY", None)
    env.update(
        PATH=f"{bin_dir}{os.pathsep}{env['PATH']}",
        RUNNER_TEMP=str(tmp_path / "runner temp"),
        GITHUB_ENV=str(tmp_path / "github-env"),
        SETUP_LOG=str(tmp_path / "setup-log"),
        FAKE_BIN=str(bin_dir),
    )
    return env


@pytest.mark.parametrize("configuration", ["unset", "empty", "configured"])
def test_poetry_setup_exports_paths_and_installs_dependencies(
    setup_environment, configuration
):
    env = setup_environment
    home = Path(env["RUNNER_TEMP"]) / "pyhpcc-poetry"
    if configuration == "empty":
        env.update(POETRY_HOME="", POETRY="")
    elif configuration == "configured":
        home = Path(env["RUNNER_TEMP"]) / "custom poetry"
        env.update(POETRY_HOME=str(home), POETRY=str(home / "bin/poetry"))

    script = Path(__file__).resolve().parents[1] / "scripts/poetry-install.sh"
    subprocess.run(["bash", str(script)], env=env, check=True)

    assert Path(env["GITHUB_ENV"]).read_text() == (
        f"POETRY_HOME={home}\nPOETRY={home}/bin/poetry\n"
    )
    assert Path(env["SETUP_LOG"]).read_text().splitlines() == [
        f"venv -m venv {home}",
        "python -m pip install poetry==1.8.3",
        "poetry install --with dev,coverage --no-interaction",
    ]


def test_poetry_setup_stops_when_venv_creation_fails(setup_environment):
    env = setup_environment
    env["FAIL_VENV"] = "1"
    script = Path(__file__).resolve().parents[1] / "scripts/poetry-install.sh"
    result = subprocess.run(["bash", str(script)], env=env, check=False)
    assert result.returncode == 7
    assert not Path(env["GITHUB_ENV"]).exists()
    assert len(Path(env["SETUP_LOG"]).read_text().splitlines()) == 1
