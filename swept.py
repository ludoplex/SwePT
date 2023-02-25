import argparse
import openai
from git import Repo
from pathlib import Path
from typing import Union

ALLOWED_FILE_EXT = [".py"]
openai.api_key = ""


def get_edits_for_instruction(code: str, instruction: str) -> str:
  response = openai.Edit.create(
    model="code-davinci-edit-001",
    input=code,
    instruction=instruction,
  )
  code = response["choices"][0]["text"]
  return code


def edit_file(file: Union[str, Path], instruction: str) -> bool:
  if isinstance(file, str):
    file = Path(file)
  with open(file) as fob:
    file_contents = fob.read()
  is_modified = False
  modified_code = get_edits_for_instruction(file_contents, instruction)

  if modified_code != file_contents:  # any more checks?
    with open(file, "w") as fob:
      fob.write(modified_code)
      is_modified = True
  else:
    print("The code was not modified!")
  return is_modified


def display_diff(repo: Repo) -> None:
  print(repo.git.diff(None))


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Edit a section of code, PR with changes.')
  parser.add_argument('-f', '--file', help='location of a file', required=True)
  parser.add_argument('-i', '--instruction', help='instruction on how to edit the file', type=str, required=True)
  parser.add_argument('-r', '--repo', help='location to git repo', type=str, default='./')
  parser.add_argument('-d', '--diff', help='show diff', action='store_true')
  parser.add_argument('-pr', '--pull-request', help='add change, commit, push and raise a PR', action='store_true')
  args = parser.parse_args()

  file = Path(args.file)
  repo_loc = Path(args.repo)
  instruction = args.instruction.strip()
  repo = Repo(repo_loc)

  assert file.exists() and file.is_file(), "File does not exist!"
  assert file.suffix in ALLOWED_FILE_EXT, "Filetype not supported"
  assert len(instruction) > 0, "Instruction not valid"
  assert not repo.bare, "Repo is bare!"

  is_modified = edit_file(file, instruction)

  if args.diff and is_modified:
    display_diff(repo)

  if args.pull_request and is_modified:
    # 1. add
    # 2. commit
    # 3. push
    # 4. pr
    pass
