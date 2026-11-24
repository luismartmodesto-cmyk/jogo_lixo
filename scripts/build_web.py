import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "build" / "web"
BROWSERFS_SCRIPT = re.compile(
    r'<script\s+src="[^"]*browserfs\.min\.js"\s*>\s*</script>',
    re.IGNORECASE,
)
BROWSERFS_SOURCEMAP = re.compile(
    r"(?:\r?\n)?//# sourceMappingURL=browserfs\.min\.js\.map\s*$"
)


def use_local_browserfs(html):
    matches = list(BROWSERFS_SCRIPT.finditer(html))
    if len(matches) != 1:
        raise RuntimeError(
            "Expected exactly one BrowserFS script tag in Pygbag's generated index.html; "
            "check the Pygbag template before building."
        )
    return BROWSERFS_SCRIPT.sub('<script src="browserfs.min.js"></script>', html, count=1)


def remove_browserfs_sourcemap_reference(source):
    return BROWSERFS_SOURCEMAP.sub("", source)


def build_web():
    with tempfile.TemporaryDirectory(prefix="missao-lixo-") as temporary_directory:
        app = Path(temporary_directory) / "missao-lixo"
        app.mkdir()
        shutil.copy2(ROOT / "main.py", app / "main.py")
        shutil.copy2(ROOT / "content.py", app / "content.py")
        shutil.copytree(ROOT / "static", app / "static")

        subprocess.run(
            [
                sys.executable,
                "-m",
                "pygbag",
                "--build",
                "--title",
                "Missão: Lixo no lugar certo",
                str(app),
            ],
            cwd=app,
            check=True,
        )

        generated = app / "build" / "web"
        index = generated / "index.html"
        browserfs = generated / "browserfs.min.js"
        if not index.is_file():
            raise FileNotFoundError("Pygbag did not generate build/web/index.html")
        if not browserfs.is_file():
            raise FileNotFoundError("Pygbag build is missing the locally bundled BrowserFS file")

        html = index.read_text(encoding="utf-8")
        index.write_text(use_local_browserfs(html), encoding="utf-8")
        browserfs_source = browserfs.read_text(encoding="utf-8")
        browserfs.write_text(
            remove_browserfs_sourcemap_reference(browserfs_source),
            encoding="utf-8",
        )

        if OUTPUT.exists():
            shutil.rmtree(OUTPUT)
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(generated, OUTPUT)

    print("Web build created at {}".format(OUTPUT))


if __name__ == "__main__":
    build_web()
