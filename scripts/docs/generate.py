#!/usr/bin/env python3

from pathlib import Path
import sys
import subprocess
from typing import List, NamedTuple, Optional, TextIO

from script_list import script_list

# Run this script whenever any of the scripts in the directory above changes.
# This will generate two files: README.md and detailed.md. The files must not
# exist beforehand, as this script won't overwrite them for safety's sake.
#
# The idea for this script is somewhat misconceived as it de facto attempts to
# parse formatted output rather than accessing argparse datastructures directly.
# It's pretty basic and does the job but there are probably better solutions,
# like sphinx-argparse, which can generate docs based on help messages (TODO).


class Script(NamedTuple):
    name: str
    help: str


def get_script_help(path: Path) -> Optional[str]:
    try:
        return subprocess.check_output(
            [path, "--help"],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
    except:
        return None


def get_scripts(path: Path) -> List[Script]:

    result: List[Script] = []

    for script in sorted(script_list):

        script_help_opt = get_script_help(script)

        if script_help_opt is not None:
            # print(f'Script "{script}" with --help succeeded.')
            result.append(
                Script(
                    script,
                    script_help_opt
                )
            )
        else:
            print(f'Running "{script.name}" with --help failed.', file=sys.stderr)

    return result


def write_full_help_to_md(output: TextIO, script: Script) -> None:
    print(
f"""# `{script.name}`

```
{script.help}
```
""",
        file=output
    )


def get_overview(script_help: str) -> str:

    result = []
    script_help_lines = iter(script_help.splitlines())

    for line in script_help_lines:
        if line == "":
            break

    for line in script_help_lines:
        if line in ("positional arguments:", "optional arguments:"):
            break
        result.append(line.strip())

    return " ".join(result)


def write_overview_to_md(output: TextIO, script: Script) -> None:
    script_overview = get_overview(script.help)
    print(
f"""## `{script.name}`

{script_overview}
""",
        file=output
    )

def write_autogen_disclaimer(output: TextIO) -> None:

    print(
f"""> **Note:** this file has been autogenerated. Do not edit manually.
""",
        file=output
    )


def write_detailed(scripts_path: Path, scripts: List[Script]) -> None:

    detailed_path = scripts_path.joinpath("detailed.md")

    with open(detailed_path, 'x') as detailed_file:

        write_autogen_disclaimer(detailed_file)

        for script in scripts:
            write_full_help_to_md(detailed_file, script)


def write_overviews(scripts_path: Path, scripts: List[Script]) -> None:

    readme_path = scripts_path.joinpath("README.md")
    # another_file = scripts_path.joinpath("docs").joinpath("another_file.md")

    with open(readme_path, 'x') as readme_file:

        write_autogen_disclaimer(readme_file)

        print(
f"""# Scripts overview

Given below are the descriptions of the provided scripts.
Full help messages can be found in the [`detailed.md`](./detailed.md) file.
""",
            file=readme_file
        )

        for script in scripts:
            write_overview_to_md(readme_file, script)

        # with open(another_file_path, 'r') as another_file:
        #     readme_file.write(another_file.read())


if __name__ == "__main__":

    this_script = sys.argv[0]
    scripts_path = Path(f"{this_script}/../../").resolve()

    scripts = get_scripts(scripts_path)

    write_detailed(scripts_path, scripts)
    write_overviews(scripts_path, scripts)
