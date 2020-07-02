import sys
from requests import get, post
from github import Github
from json import dumps

def validate_inputs():
    # Returns a dict of inputs needed to make requests to GitHub
    if len(sys.argv) == 4:
        token = sys.argv[1]
        owner = sys.argv[2]
        repo = sys.argv[3]
    else:
        print('Error: This script requires three inputs, GITHUB_TOKEN, OWNER, and REPO, but only %d were provided').format(len(sys.argv)-1)
        exit(1)
    return { 'token': token, 'owner': owner, 'repo': repo }

def get_open_prs(input):
    # Returns the first page of open PR's for the target repo
    headers = {"Authorization": 'token {}'.format(input['token']), "Accept": "application/vnd.github.v3+json"}
    url = 'https://api.github.com/repos/{}/{}/pulls?state=open&page=1'.format(input['owner'], input['repo'])
    resp = get(url,headers=headers)
    return resp

def paginate(input, resp):
    # Returns all open PR's for the target repo using pagination
    # This is needed because only 30 PR's are returned by default per page
    while 'next' in resp.links.keys():
        headers = {"Authorization": 'token {}'.format(input['token'])}
        next_prs = get(resp.links['next']['url'],headers=headers)
        resp.json().extend(next_prs.json())
    return resp.json()

def get_pr_numbers(resp):
    # Return an array of PR numbers when the target branch == master
    # These PR numbers are needed in the request to update the target branch
    numbers = []
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
    pr_url = 'https://github.com/{}/{}/pull'.format(input['owner'], input['repo'])
    for pr_number in numbers:
        try:
            # https://developer.github.com/v3/pulls/#update-a-pull-request
            url = 'https://api.github.com/repos/{}/{}/pulls/{}'.format(input['owner'], input['repo'], pr_number)
            payload = { 'base': 'main' }
            headers = { 'Authorization': 'token {}'.format(input['token']), 'Accept': 'application/vnd.github.v3+json' }
            res = post(url,data=dumps(payload),headers=headers)
            res.raise_for_status()
            print('Success: Updated target branch for the following PR: {}/{}'.format(pr_url, pr_number))
        except Exception as e:
            # Send slack notification - couldn't upate 
            print('Error: Failed to update target branch for the following PR: {}/{}'.format(pr_url, pr_number))
            raise(e)


input = validate_inputs()
prs = get_open_prs(input)
paginate(input, prs)
numbers = get_pr_numbers(prs)
update_pr_target_branch(input, numbers)
