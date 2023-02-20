#!/usr/bin/env python3

import argparse
# import json
import sys
from pathlib import Path
from typing import Optional

import requests

import lib.base3
import lib.shell3


__author__ = 'Navid Sassan'
__version__ = '2023022004'

DESCRIPTION = """A script that clones all the starred repos of the given GitHub user."""

def parse_args():
    """Parse command line arguments using argparse.
    """
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument(
        '-V', '--version',
        action='version',
        version='%(prog)s: v{} by {}'.format(__version__, __author__)
    )

    parser.add_argument(
        '--base-dir',
        help='Path of the base directory under which the repos will be cloned (subfolder for owner and repo name will be created).',
        dest='BASE_DIR',
        required=True,
    )

    parser.add_argument(
        '--username',
        help='The GitHub user whose stars will be cloned.',
        dest='USERNAME',
        required=True,
    )

    parser.add_argument(
        '--token',
        help='GitHub API token. Use this when running into API rate limits.',
        dest='TOKEN',
    )

    return parser.parse_args()


def get_stars(username: str, auth_token: Optional[str] = None, page: int = 1) -> list:
    headers = {}
    if auth_token:
        headers = {
            'Authorization': f'Bearer {auth_token}',
        }
    r = requests.get(
        f'https://api.github.com/users/{username}/starred',
        headers=headers,
        params={
            'per_page': 100, # this is the max
            'page': page,
        },
    )
    stars = r.json()
    if isinstance(stars, dict) and 'rate limit' in stars.get('message', ''):
        print('hit the github api rate limit')
        print(r.json())
        sys.exit(1)

    # end condition
    if not len(stars):
        return list(stars)

    return list(stars) + get_stars(username, auth_token=auth_token, page=page+1)


def main():
    args = parse_args()

    stars = get_stars(args.USERNAME, args.TOKEN)

    # use this for testing while avoiding the api rate limit
    # with open('/tmp/stars.json', 'w') as f:
    #     json.dump(
    #         stars,
    #         f,
    #         indent=4,
    #     )
    #     f.write('\n')
    #
    # with open('/tmp/stars.json', 'r') as f:
    #     stars = json.load(f)

    print(f'Found {len(stars)} stars for {args.USERNAME}.')

    errors = False
    count = 1
    for star in stars:
        count += 1
        repo_path = Path(args.BASE_DIR, star['owner']['login'])
        if not Path(args.BASE_DIR).resolve() in repo_path.resolve().parents:
            print(f"ERROR: Filename {repo_path} is not in {Path(args.BASE_DIR)} directory. Skipping Repo {star['full_name']}.")
            errors = True
            continue

        try:
            repo_path.mkdir(parents=True)
        except FileExistsError:
            pass

        print(f'Cloning {star["full_name"]} ({count}/{len(stars)})...')
        cmd = f"git clone --mirror '{star['clone_url']}'"
        stdout, stderr, retc = lib.base3.coe(lib.shell3.shell_exec(cmd, cwd=repo_path))
        if retc != 0 and not 'already exists' in stderr:
            print(f'ERROR: Command "{cmd}" failed with {retc} and:\n{stdout}\n{stderr}')
            errors = True
            continue

    if errors:
        sys.exit(2)

if __name__ == '__main__':
    main()
