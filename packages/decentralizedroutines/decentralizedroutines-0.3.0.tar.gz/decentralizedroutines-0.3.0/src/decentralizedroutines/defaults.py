import os 

if not 'GIT_SERVER' in os.environ:
    os.environ['GIT_SERVER']='github.com'

if not 'REPO_FOLDER' in os.environ:
    os.environ['REPO_FOLDER'] = os.environ['USERPROFILE']+'\\src\\'

if not 'SLEEP_TIME' in os.environ:    
    os.environ['SLEEP_TIME'] = 5

os.environ['USER_COMPUTER'] = os.environ['USERNAME']+'@'+os.environ['COMPUTERNAME']