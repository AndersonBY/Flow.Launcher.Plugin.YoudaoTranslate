import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DIST_DIR = ROOT / "dist"
PACKAGE_DIR = DIST_DIR / "run"
PACKAGE_NAME = "Flow.Launcher.Plugin.YoudaoTranslate"
RUNTIME_PATHS = (
    "run.py",
    "plugin",
    "assets",
    "translations",
    "plugin.json",
    "SettingsTemplate.yaml",
)


def run_command(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def copy_runtime_files() -> None:
    for relative_path in RUNTIME_PATHS:
        source = ROOT / relative_path
        destination = PACKAGE_DIR / relative_path
        if source.is_dir():
            shutil.copytree(
                source,
                destination,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
            )
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)


def install_runtime_dependencies() -> None:
    requirements_path = DIST_DIR / "requirements.txt"
    run_command(
        [
            "pdm",
            "export",
            "--prod",
            "--without-hashes",
            "--format",
            "requirements",
            "--output",
            str(requirements_path),
        ]
    )
    run_command(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--ignore-installed",
            "--no-compile",
            "--no-warn-conflicts",
            "--requirement",
            str(requirements_path),
            "--target",
            str(PACKAGE_DIR / "lib"),
        ]
    )


def remove_generated_files() -> None:
    scripts_dir = PACKAGE_DIR / "lib" / "bin"
    if scripts_dir.exists():
        shutil.rmtree(scripts_dir)

    for path in PACKAGE_DIR.rglob("__pycache__"):
        shutil.rmtree(path)
    for pattern in ("*.pyc", "*.pyo"):
        for path in PACKAGE_DIR.rglob(pattern):
            path.unlink()


def build_source_package() -> Path:
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    PACKAGE_DIR.mkdir(parents=True)

    copy_runtime_files()
    install_runtime_dependencies()
    remove_generated_files()

    archive = shutil.make_archive(str(DIST_DIR / PACKAGE_NAME), "zip", PACKAGE_DIR)
    return Path(archive)


if __name__ == "__main__":
    print(build_source_package())
