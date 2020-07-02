import requests, sys

token = sys.argv[1]
org = sys.argv[2]
repo = sys.argv[3]

get_open_prs = 'https://api.github.com/repos/%s/%s/pulls?state=open&page=1'.format(org, repo)
res=requests.get(get_open_prs,headers={"Authorization": token, "Accept": "application/vnd.github.v3+json"})
prs=res.json()
print(prs)
# while 'next' in res.links.keys():
#   res=requests.get(res.links['next']['url'],headers={"Authorization": git_token})
#   repos.extend(res.json())

# set -e

# curl -H "Authorization: token $1" -H "Accept: 'application/vnd.github.v3+json'" "https://api.github.com/repos/$2/$3/pulls?state=open" -o open_prs.txt

# echo hello.txt
