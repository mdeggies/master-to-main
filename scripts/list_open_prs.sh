set -e

curl -H "Authorization: token $1" -H "Accept: 'application/vnd.github.v3+json'" "https://api.github.com/repos/$2/$3/pulls?state=open" -O hello.txt

echo hello.txt
