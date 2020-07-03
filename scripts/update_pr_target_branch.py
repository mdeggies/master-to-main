from sys import argv
from requests import get, post
from github import Github
from json import dumps
from logging import basicConfig, info, error, DEBUG

def validate_inputs():
    # Returns a dict of inputs needed to make requests to GitHub
    if len(argv) == 4:
        token = argv[1]
        owner = argv[2]
        repo = argv[3]
        repo_url = 'https://github.com/{}/{}'.format(owner, repo)
        api_url = 'https://api.github.com/repos/{}/{}'.format(owner, repo)
    else:
        error('Error: This script requires three inputs, GITHUB_TOKEN, OWNER, and REPO, but only %d were provided').format(len(argv)-1)
        exit(1)
    return { 'token': token, 'owner': owner, 'repo': repo }

def get_open_prs(input):
    # Returns the first page of open PR's for the target repo
    headers = {"Authorization": 'token {}'.format(input['token']), "Accept": "application/vnd.github.v3+json"}
    url = '{}/pulls?state=open&page=1'.format(input['api_url'])
    try:
        resp = get(url,headers=headers)
    except Exception as e:
        error('Failed to get first page of open PRs for repo: {}'.format(input['repo_url']))
        raise(e)
    return resp

def paginate(input, resp):
    # Returns all open PR's for the target repo using pagination
    # This is needed because only 30 PR's are returned by default per page
    while 'next' in resp.links.keys():
        headers = {"Authorization": 'token {}'.format(input['token'])}
        try:
            next_prs = get(resp.links['next']['url'],headers=headers)
            resp.json().extend(next_prs.json())
        except Exception as e:
            error('Failed to get all open PRs for repo: {}'.format(input['repo_url']))
            raise(e)
    return resp.json()

def get_pr_numbers(resp):
    # Return an array of PR numbers when the target branch == master
    # These PR numbers are needed in the request to update the target branch
    numbers = []
    info('There are {} open PRs with a master target branch to update in repo {}'.format(len(resp.json()), input['repo_url']))
    for pr in resp.json():
        if 'base' in pr:
            base = pr['base']
            if 'ref' in base:
                target_branch = base['ref']
        if 'master' == target_branch:
            if 'number' in pr:
                numbers.append(pr['number'])
    return numbers

def update_pr_target_branch(input, numbers):
    # Update the target branch on open PR's from 'master' to 'main'
    # https://developer.github.com/v3/pulls/#update-a-pull-request
    pr_url = '{}/pull'.format(input['repo_url'])
    for pr_number in numbers:
        try:
            url = '{}/pulls/{}'.format(input['api_url'], pr_number)
            payload = { 'base': 'main' }
            headers = { 'Authorization': 'token {}'.format(input['token']), 'Accept': 'application/vnd.github.v3+json' }
            res = post(url,data=dumps(payload),headers=headers)
            res.raise_for_status()
            info('Success: Updated target branch for the following PR: {}/{}'.format(pr_url, pr_number))
        except Exception as e:
            error('Error: Failed to update target branch for the following PR: {}/{}'.format(pr_url, pr_number))
            raise(e)

basicConfig(level=DEBUG)

input = validate_inputs()
prs = get_open_prs(input)
paginate(input, prs)
numbers = get_pr_numbers(prs)
update_pr_target_branch(input, numbers)
