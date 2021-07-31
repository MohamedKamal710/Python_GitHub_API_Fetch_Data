import requests
import pymysql.cursors
from requests.auth import HTTPBasicAuth


# TODO put your username password
connection = pymysql.connect(host="localhost",
                             user="root",
                             password="root",
                             db="github_software",
                             charset="utf8mb4",
                             cursorclass=pymysql.cursors.DictCursor)


def executeSelect(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        connection.commit()
        result = cursor.fetchall()
        return result


def executeInsert(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        connection.commit()
        return cursor.lastrowid


## Get all valid repositories with stars and watchers and forks count
## In this method , we iterate through every repository and check its url validity.
## a valid url leads to inclusion of the repository in a format we desire (Where we get Stars, Watchers and forks count).
## @OriginalId is the id in the dataset (in case it is different that the id in the Github API)
## @Originals as the original repository table
def getRepos():
    res = executeSelect("""SELECT id, url FROM  originals;""")
    r = 0;
    c = 1;
    tokenName = 'TypeYourGitHubNameHere'
    tokenKey = 'YourGithubToken'
    for i in res:
        try:
            forked_from = -1;
            if 'forked_from' in i:
                forked_from = i['forked_from'];
            url = i['url'];
            originalid = i['id'];
            res2 = requests.get(f'{url}',
                               auth=HTTPBasicAuth(tokenName, tokenKey))
            json = res2.json()
            r+=1;
            j = r;
            if('message' in json):
                print("INVALID JSON ")
                print(json)
                if(json['documentation_url'] == 'https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting' ):
                    if(tokenName == 'TypeYourGitHubNameHere'):      ## Here we are switching between the tokens so the script won't stop excuting , because one token has a limited use.
                        tokenName = 'TypeYourGitHubNameHere'
                        tokenKey = 'YourGithubToken'
                    else:
                        tokenName = 'TypeYourGitHubNameHere'        ##Switch Tokens here too
                        tokenKey = 'YourGithubToken'
            if('message' not in json):
                c += 1;
                print(json)
                print(c);
                w = json['subscribers_count']
                desc = json['description']
                if desc:
                    desc = desc.replace('\'', '')
                insert = f"""INSERT IGNORE INTO `repos`
                (`id`, `url`, `owner_id`, `name`, `description`,
                `language`, `created_at`, `forked_from`, `watchers`,`stars`,`forks_count`,`deleted`,
                 `updated_at`, `original_id`)
                 VALUES ({json['id']},'{json['url']}' , {json['owner']['id']},
                    '{json['name']}','{desc}','{json['language']}' ,
                    '{json['created_at']}', {forked_from}, {w}, {json['stargazers_count']},{json['forks']},0,'{json['updated_at']}', {originalid});"""
                print(insert)
                executeInsert(insert)
        except:
            continue

## Get all forked projects .
## In this method we iterate through every repository to get their children and Insert them in a table in the database.
## We include stars, watchers, and the commits count.
# @repos as the source table of the repositories (Parents i.e. Forkees).
def getForks():
    res = executeSelect("""SELECT id, url FROM  repos p where forks_count>0""")
    c = 0;
    flag = 0;
    tokenName1 = 'TypeYourGitHubNameHere'
    tokenKey1 = 'YourGithubToken'

    tokenName2 = 'TypeYourGitHubNameHere'
    tokenKey2 = 'YourGithubToken'

    tokenName3 = 'TypeYourGitHubNameHere'
    tokenKey3 = 'YourGithubToken'

    tokenName4 = 'TypeYourGitHubNameHere'
    tokenKey4 = 'YourGithubToken'

    for i in res:
        try:
            print("*")

            forked_from = -1;
            url = i['url'];
            forked_from = i['id'];
            res2 = requests.get(f'{url}',
                               auth=HTTPBasicAuth(tokenName1, tokenKey1))
            json = res2.json()

            if ('message' in json):
                print("INVALID JSON ")
                print(json)
                if (json[
                    'documentation_url'] == 'https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting'):
                    flag = 1;
                    if (tokenName1 == 'TypeYourGitHubNameHere'):   ## Here we are switching between the tokens so the script won't stop excuting , because one token has a limited use.
                        tokenName1 = 'TypeYourGitHubNameHere'
                        tokenKey1 = 'YourGithubToken'
                    else:                                           ## Switch Tokens here too
                        tokenName1 = 'TypeYourGitHubNameHere'
                        tokenKey1 = 'YourGithubToken'

            if ('message' not in json):
                forks_url = json['forks_url'];
                print(forks_url)
                res3 = requests.get(f'{forks_url}',
                                    auth=HTTPBasicAuth(tokenName2, tokenKey2))
                json2 = res3.json()
                for child in json2:

                        if ('message' in child):
                            print("INVALID CHILD ")
                            print(json)
                            if (child[
                                'documentation_url'] == 'https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting'):
                                flag = 1;
                                if (tokenName2 == 'TypeYourGitHubNameHere'):
                                    tokenName2 = 'TypeYourGitHubNameHere'
                                    tokenKey2 = 'YourGithubToken'
                                else:
                                    tokenName2 = 'TypeYourGitHubNameHere'
                                    tokenKey2 = 'YourGithubToken'

                        if ('message' not in child):
                            print("VALID CHILD")
                            repo_full_name = child['full_name']
                            res3 = requests.get(f'https://api.github.com/repos/{repo_full_name}/subscribers',
                                                auth=HTTPBasicAuth(tokenName3, tokenKey3))
                            watchers_json = res3.json()
                            for watch in watchers_json:
                                if ('message' in watch):
                                    print("INVALID WATCHERS ")
                                    print(json)
                                    if (watch['documentation_url'] == 'https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting'):
                                        flag = 1;
                                        if (tokenName3 == 'TypeYourGitHubNameHere'):     ## Here we are switching between the tokens so the script won't stop excuting , because one token has a limited use.
                                            tokenName3 = 'TypeYourGitHubNameHere'
                                            tokenKey3 = 'YourGithubToken'
                                        else:                                             ## Switch Tokens here too
                                            tokenName3 = 'TypeYourGitHubNameHere'
                                            tokenKey3 = 'YourGithubToken'
                                else: break;

                            res4 = requests.get(f'https://api.github.com/repos/{repo_full_name}/commits',
                                                auth=HTTPBasicAuth(tokenName4, tokenKey4))
                            commits_json = res4.json()
                            for commit in commits_json:
                                if ('message' in commit):
                                    print("INVALID Commiters ")
                                    print(json)
                                    if (commit[
                                        'documentation_url'] == 'https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting'):
                                        flag = 1;
                                        if (tokenName4 == 'TypeYourGitHubNameHere'):   ## Here we are switching between the tokens so the script won't stop excuting , because one token has a limited use.
                                            tokenName4 = 'TypeYourGitHubNameHere'
                                            tokenKey4 = 'YourGithubToken'
                                        else:
                                            tokenName4 = 'TypeYourGitHubNameHere'     ## Switch Tokens here too
                                            tokenKey4 = 'YourGithubToken'
                                else:
                                    break;


                            if(flag==0):
                                w = len(watchers_json)
                                commits = len(commits_json)
                                print("***")
                                c+=1;
                                desc = child['description']
                                if desc:
                                    desc = desc.replace('\'', '')
                                forks = -1;
                                if('fork' in child):
                                    forks = child['forks']
                                insert = f"""INSERT IGNORE INTO `forks_`
                                        (`id`, `url`, `owner_id`, `name`, `description`,
                                        `language`, `created_at`, `forked_from`, `watchers`,`stars`,`forks_count`,`deleted`,
                                         `updated_at`, `commits_count`)
                                         VALUES ({child['id']},'{child['url']}' , {child['owner']['id']},
                                            '{child['name']}','{desc}','{child['language']}' ,
                                            '{child['created_at']}', {forked_from}, {w}, {child['stargazers_count']},{forks},0,'{child['updated_at']}', {commits});"""
                                print(insert)
                                print(c);
                                executeInsert(insert)
                            if(flag==1):
                                flag=0;
        except:
            continue


## Get all pull requests which are related to the forkees.
## @repos as the repository table
def getPullsFromParents():

    res = executeSelect("""SELECT r.id, r.url, r.name FROM  repos r
        WHERE r.forks_count>0;""")

    flag = 0;
    tokenName1 = 'TypeYourGitHubNameHere'   # Here you put your github username
    tokenKey1 = 'YourGithubToken'           # Here you put your generated github token

    tokenName2 = 'TypeYourGitHubNameHere'   # Here you put another github username
    tokenKey2 = 'YourGithubToken'           # Here you put another generated github token

    for i in res:
        url = i['url']
        repo_id = i['id']
        repo_name = i['name']


        res2 = requests.get(f'{url}/pulls',
                            auth=HTTPBasicAuth(tokenName1, tokenKey1))
        json = res2.json()
        print("?>")
        print(url)

        for repo in json:
            if ('message' in json):
                print("INVALID JSON ")
                print(json)
                if (json[
                    'documentation_url'] == 'https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting'):
                    flag = 1;
                    if (tokenName1 == 'TypeYourGitHubNameHere'):   ## Here we are switching between the tokens so the script won't stop excuting , because one token has a limited use.
                        tokenName1 = 'TypeYourGitHubNameHere'
                        tokenKey1 = 'YourGithubToken'
                    else:
                        tokenName1 = 'TypeYourGitHubNameHere'     ## Switch Tokens here too
                        tokenKey1 = 'YourGithubToken'

            if ('message' not in json):
                print("----------------------------------------")
                print(repo)
                head = -1;
                base = -1;
                if (repo is not None and repo['head'] is not None and repo['head']['repo'] is not None):
                    head = repo['head']['repo']['id'];
                    print(repo['head']['repo']['id'])
                if (repo is not None and repo['base'] is not None and repo['base']['repo'] is not None):
                    base = repo['base']['repo']['id'];
                    print(repo['base']['repo']['id'])

                print("----------------------------------------")

                site = repo['commits_url']
                res4 = requests.get(f'{site}',
                                    auth=HTTPBasicAuth(tokenName2, tokenKey2))
                commits_json = res4.json()
                c=-1;
                if ('message' in commits_json):
                    print("INVALID CHILD ")
                    print(commits_json)
                    if (commits_json[
                        'documentation_url'] == 'https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting'):
                        flag = 1;
                        if (tokenName2 == 'TypeYourGitHubNameHere'):   ## Here we are switching between the tokens so the script won't stop excuting , because one token has a limited use.
                            tokenName2 = 'TypeYourGitHubNameHere'
                            tokenKey2 = 'YourGithubToken'
                        else:
                            tokenName2 = 'TypeYourGitHubNameHere'     ## Switch Tokens here too
                            tokenKey2 = 'YourGithubToken'

                if('message' not in commits_json):
                    c = len(commits_json)
                desc = ''

                if desc in repo:
                    desc = connection.escape_string(repo['description'])
                insert = f"""INSERT IGNORE INTO `pulls`
                    (`id`, `url`, `owner_id`, `name`, `forked_from`, `num_of_commits`,`head_id`, `base_id`)
                    VALUES ({repo['id']},'{repo['url']}' , {repo['user']['id']}, '{repo_name}', {repo_id}, {c}, {head} ,{base});"""
                print(insert)
                executeInsert(insert)


## Retrieve all the pull requests which are related to the forked projects.
## @Forks_ as the forks table
def getPullsFromChildren():

    res = executeSelect("""SELECT f.id, f.url, f.name FROM  forks_ f;""")

    flag = 0;
    tokenName1 = 'TypeYourGitHubNameHere'  # Here you put your github username
    tokenKey1 = 'YourGithubToken'          # Here you put your generated github token

    tokenName2 = 'TypeYourGitHubNameHere'   # Here you put another github username
    tokenKey2 = 'YourGithubToken'           # Here you put another generated github token

    for i in res:
        url = i['url']
        repo_id = i['id']
        repo_name = i['name']


        res2 = requests.get(f'{url}/pulls',
                            auth=HTTPBasicAuth(tokenName1, tokenKey1))
        json = res2.json()
        print("?>")
        print(url)

        for repo in json:
            if ('message' in json):
                print("INVALID JSON ")
                print(json)
                if (json[
                    'documentation_url'] == 'https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting'):
                    flag = 1;
                    if (tokenName1 == 'TypeYourGitHubNameHere'):  ## Here we are switching between the tokens so the script won't stop excuting , because one token has a limited use.
                        tokenName1 = 'TypeYourGitHubNameHere'
                        tokenKey1 = 'YourGithubToken'
                    else:
                        if (tokenName1 == 'TypeYourGitHubNameHere'):     ## Switch Tokens here too
                            tokenName1 = 'TypeYourGitHubNameHere'
                            tokenKey1 = 'YourGithubToken'
                        else:
                            if(tokenName1 == 'TypeYourGitHubNameHere'):     ## Switch Tokens here too
                                tokenName1 == 'TypeYourGitHubNameHere'
                                tokenKey1 = 'YourGithubToken'

            if ('message' not in json):
                print("----------------------------------------")
                print(repo)
                head = -1;
                base = -1;
                if (repo is not None and repo['head'] is not None and repo['head']['repo'] is not None):
                    head = repo['head']['repo']['id'];
                    print(repo['head']['repo']['id'])
                if (repo is not None and repo['base'] is not None and repo['base']['repo'] is not None):
                    base = repo['base']['repo']['id'];
                    print(repo['base']['repo']['id'])

                print("----------------------------------------")

                site = repo['commits_url']
                res4 = requests.get(f'{site}',
                                    auth=HTTPBasicAuth(tokenName2, tokenKey2))
                commits_json = res4.json()
                c=-1;
                if ('message' in commits_json):
                    print("INVALID CHILD ")
                    print(commits_json)
                    if (commits_json[
                        'documentation_url'] == 'https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting'):
                        flag = 1;
                        if (tokenName2 == 'TypeYourGitHubNameHere'):   ## Here we are switching between the tokens so the script won't stop excuting , because one token has a limited use.
                            tokenName2 = 'TypeYourGitHubNameHere'
                            tokenKey2 = 'YourGithubToken'
                        else:
                            if (tokenName2 == 'TypeYourGitHubNameHere'):  ## Switch Tokens here too
                                tokenName2 = 'TypeYourGitHubNameHere'
                                tokenKey2 = 'YourGithubToken'
                            else:
                                if (tokenName2 == 'TypeYourGitHubNameHere'):  ## Switch Tokens here too
                                    tokenName2 == 'TypeYourGitHubNameHere'
                                    tokenKey2 = 'YourGithubToken'


                if('message' not in commits_json):
                    c = len(commits_json)
                desc = ''

                if desc in repo:
                    desc = connection.escape_string(repo['description'])
                insert = f"""INSERT IGNORE INTO `pulls`
                    (`id`, `url`, `owner_id`, `name`, `forked_from`, `num_of_commits`,`head_id`, `base_id`)
                    VALUES ({repo['id']},'{repo['url']}' , {repo['user']['id']}, '{repo_name}', {repo_id}, {c}, {head} ,{base});"""
                print(insert)
                executeInsert(insert)

## This method takes the forked projects in our database and returns them in a different format (different fields)
## It validates and removes deleted forks, it Also adds stars, watchers and commits count.
def updateForks():
    res = executeSelect("""SELECT id, url FROM  forks_;""")
    r = 0;
    c = 1;
    flag=0;
    invalidComitts = 0;
    tokenName = 'TypeYourGitHubNameHere'
    tokenKey = 'YourGithubToken'

    tokenName2 = 'TypeYourGitHubNameHere'
    tokenKey2 = 'YourGithubToken'
    for i in res:
        try:
            forked_from = -1;
            if 'forked_from' in i:
                forked_from = i['forked_from'];
            url = i['url'];
            originalid = i['id'];
            res2 = requests.get(f'{url}',
                               auth=HTTPBasicAuth(tokenName, tokenKey))
            json = res2.json()
            r+=1;
            j = r;
            if('message' in json):
                print("INVALID JSON ")
                print(json)
                if(json['documentation_url'] == 'https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting' ):
                    if(tokenName == 'TypeYourGitHubNameHere'):       ## Here we are switching between the tokens so the script won't stop excuting , because one token has a limited use.
                        tokenName = 'TypeYourGitHubNameHere'
                        tokenKey = 'YourGithubToken'
                    else:
                        tokenName = 'TypeYourGitHubNameHere'          ## Switch Tokens here too
                        tokenKey = 'YourGithubToken'
            if('message' not in json):

                res4 = requests.get(f'{url}/commits',
                                    auth=HTTPBasicAuth(tokenName2, tokenKey2))
                commits_json = res4.json()
                for commit in commits_json:
                    if ('message' in commit):
                        print("INVALID Commiters ")
                        print(commits_json)
                        invalidComitts+=1;
                        if (commit[
                            'documentation_url'] == 'https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting'):
                            flag = 1;
                            if (tokenName2 == 'TypeYourGitHubNameHere'):      ## Here we are switching between the tokens so the script won't stop excuting , because one token has a limited use.
                                tokenName2 = 'TypeYourGitHubNameHere'
                                tokenKey2 = 'YourGithubToken'
                            else:
                                tokenName2 = 'TypeYourGitHubNameHere'         ## Switch Tokens here too
                                tokenKey2 = 'YourGithubToken'
                    else:
                        break;
                if(flag==0):
                    c += 1;
                    print(f'number of comitts: {invalidComitts}');
                    print(json)
                    print(c);
                    commits = len(commits_json)
                    w = json['subscribers_count']

                    desc = json['description']
                    if desc:
                        desc = desc.replace('\'', '')
                    insert = f"""INSERT IGNORE INTO `forks`
                    (`id`, `url`, `owner_id`, `name`, `description`,
                    `language`, `created_at`, `forked_from`, `watchers`,`stars`,`forks_count`,`deleted`,
                     `updated_at`, `original_id`, `commits_count`)
                     VALUES ({json['id']},'{json['url']}' , {json['owner']['id']},
                        '{json['name']}','{desc}','{json['language']}' ,
                        '{json['created_at']}', {forked_from}, {w}, {json['stargazers_count']},{json['forks']},0,'{json['updated_at']}', {originalid}, {commits});"""
                    print(insert)
                    executeInsert(insert)
                if (flag == 1):
                    flag = 0;
        except:
            continue

#################################################################################################################################
#################################################################################################################################
## Functions that were used to get the dumped dataset, as for dataset 1 and dataset 2, we didn't use the following functions.
def users():
    res = requests.get(f'https://api.github.com/users',
                           auth=HTTPBasicAuth('TypeYourGitHubNameHere', 'YourGithubToken'))
    json = res.json()
    print(json)
    for user in json:
        print(user)
        login=user['login']
        executeInsert(f'INSERT IGNORE INTO users VALUES ({user["id"]}, "{login}")')


## Get repositories that are realted to certain users.
def getReposFromUsers():
    res = executeSelect("""SELECT id, login FROM  users u;""")
    for i in res:
        username = i['login']
        userId = i['id']
        res2 = requests.get(f'https://api.github.com/users/{username}/repos?per_page=100',
                           auth=HTTPBasicAuth('TypeYourGitHubNameHere', 'YourGithubToken'))
        json = res2.json()
        for repo in json:
            repo_full_name=repo['full_name']
            res3=requests.get(f'https://api.github.com/repos/{repo_full_name}/subscribers',
                              auth=HTTPBasicAuth('TypeYourGitHubNameHere', 'YourGithubToken'))
            watchers_json=res3.json()
            w=len(watchers_json)
            print(w)
            print(watchers_json)
            print(repo['watchers'])
            forked_from = 0
            if 'forked_from' in repo:
                forked_from = repo['forked_from']
            desc = repo['description']
            if desc:
                desc = desc.replace('\'', '')
            insert = f"""INSERT IGNORE INTO `repos`
            (`id`, `url`, `owner_id`, `name`, `description`, 
            `language`, `created_at`, `forked_from`, `watchers`,`stars`,`forks_count`,`deleted`,
             `updated_at`) 
             VALUES ({repo['id']},'{repo['url']}' , {userId}, 
                '{repo['name']}','{desc}','{repo['language']}' ,
                '{repo['created_at']}', {forked_from}, {w}, {repo['stargazers_count']},{repo['forks']},0,'{repo['updated_at']}');"""
            print(insert)
            executeInsert(insert)


## Get forked projects that are related to the repositories which will be extracted in the above method.
## Where the
def GetForksFromRepos():
    res = executeSelect("""SELECT u.id as userID,u.login,p.id,p.name FROM  users u
    INNER JOIN repos p ON u.id = p.owner_id
    ORDER BY `stars` DESC;""")
    for i in res:
        user_id=i['userID']
        username = i['login']
        repo_name = i['name']
        repo_id = i['id']
        print(repo_id)
        res2 = requests.get(f'https://api.github.com/repos/{username}/{repo_name}/forks',
                           auth=HTTPBasicAuth('TypeYourGitHubNameHere', 'YourGithubToken'))
        json = res2.json()
        print(json)
        for repo in json:
            repo_full_name = repo['full_name']
            res3 = requests.get(f'https://api.github.com/repos/{repo_full_name}/subscribers',
                                auth=HTTPBasicAuth('TypeYourGitHubNameHere', 'YourGithubToken'))
            watchers_json = res3.json()
            w = len(watchers_json)

            res4 = requests.get(f'https://api.github.com/repos/{repo_full_name}/commits',
                                auth=HTTPBasicAuth('TypeYourGitHubNameHere', 'YourGithubToken'))
            commits_json = res4.json()
            c= -1;
            if('message' in commits_json):
                c = len(commits_json)
            desc=''
            if desc in repo:
                desc=connection.escape_string(repo['description'])
            insert = f"""INSERT IGNORE INTO `forks`
            (`id`, `url`, `owner_id`, `name`, `description`, 
            `language`, `created_at`, `forked_from`, `watchers`,`stars`,`forks_count`, `deleted`,`num_of_commits`,
             `updated_at`) 
             VALUES ({repo['id']},'{repo['url']}' , {repo['owner']['id']}, 
                '{repo['name']}','{desc}','{repo['language']}' ,
                '{repo['created_at']}', {repo_id}, {w}, {repo['stargazers_count']},{repo['forks']},0,{c},'{repo['updated_at']}, {c}');"""
            print(insert)
            executeInsert(insert)

## Get all pull requests that are related to the previous Forked projects and their forkees.
def pull_request():
    res = executeSelect("""SELECT u.id as userID,u.login,p.id,p.name FROM  users u
        INNER JOIN repos p ON u.id = p.owner_id
        ORDER BY `stars` DESC;""")
    for i in res:
        user_id = i['userID']
        username = i['login']
        repo_name = i['name']
        # father id
        repo_id = i['id']
        print(repo_id)
                                                # TO DO FROM HERE

        res2 = requests.get(f'https://api.github.com/repos/{username}/{repo_name}/pulls',
                            auth=HTTPBasicAuth('TypeYourGitHubNameHere', 'YourGithubToken'))
        json = res2.json()
        print(json)

        for repo in json:
            if(repo!="message" and repo!="block" and repo!="html_url" and len(repo)>30):
                print(repo)
                site=repo['commits_url']
                res4 = requests.get(f'{site}',
                        auth=HTTPBasicAuth('TypeYourGitHubNameHere', 'YourGithubToken'))
                commits_json = res4.json()
                c = len(commits_json)
                desc = ''
                head = -1;
                if(repo['head']['repo'] is not None):
                    head = repo['head']['repo']['id'];

                base = -1;
                if (repo['base']['repo'] is not None):
                    base = repo['base']['repo']['id'];

                if desc in repo:
                    desc = connection.escape_string(repo['description'])
                insert = f"""INSERT IGNORE INTO `pulls`
                    (`id`, `url`, `owner_id`, `name`, `forked_from`, `num_of_commits`,`head_id`, `base_id`)
                    VALUES ({repo['id']},'{repo['url']}' , {repo['user']['id']}, '{repo_name}', {repo_id}, {c}, {head} ,{base});"""
                print(insert)
                executeInsert(insert)


## just a random test.
def test():
        username = "saymedia"
        userId = 53830
        res2 = requests.get(f'https://api.github.com/users/{username}/repos?per_page=100',
                            auth=HTTPBasicAuth('TypeYourGitHubNameHere', 'YourGithubToken'))
        json = res2.json()
        print(json);
        for repo in json:
            repo_full_name = repo['full_name']
            res3 = requests.get(f'https://api.github.com/repos/{repo_full_name}/subscribers',
                                auth=HTTPBasicAuth('TypeYourGitHubNameHere', 'YourGithubToken'))
            watchers_json = res3.json()
            w = len(watchers_json)
            print(w)
            print(watchers_json)
            print(repo['watchers'])
            forked_from = 0
            if 'forked_from' in repo:
                forked_from = repo['forked_from']
            desc = repo['description']
            if desc:
                desc = desc.replace('\'', '')
            insert = f"""INSERT IGNORE INTO `repos`
            (`id`, `url`, `owner_id`, `name`, `description`, 
            `language`, `created_at`, `forked_from`, `watchers`,`stars`,`forks_count`,`deleted`,
             `updated_at`) 
             VALUES ({repo['id']},'{repo['url']}' , {userId}, 
                '{repo['name']}','{desc}','{repo['language']}' ,
                '{repo['created_at']}', {forked_from}, {w}, {repo['stargazers_count']},{repo['forks']},0,'{repo['updated_at']}');"""


#################################################################################################################################
#################################################################################################################################
## Functions that were used to get the dumped dataset, as for dataset 1 and dataset 2, we didn't use the above functions.


updateForks();


