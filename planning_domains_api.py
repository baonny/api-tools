
import httplib, urllib, json, os, re
import xml.etree.ElementTree as etree

URL = 'api.planning.domains'
VERSION = '0.2'

DOMAIN_PATH = False
USER_EMAIL = False
USER_TOKEN = False

def checkForDomainPath():
    """Returns the domain path if one exists and is saved in the settings.xml"""

    home_dir = os.path.expanduser("~")
    pd_dir = os.path.join(home_dir,".planning.domains")
    settingsXML = os.path.join(pd_dir,"settings.xml")

    if not os.path.isdir(pd_dir) or not os.path.isfile(settingsXML):
        return False

    installationTree = etree.parse(settingsXML)
    if installationTree is None:
        return False

    installationSettings = installationTree.getroot()
    if installationSettings is None:
        return False

    domainPath = filter(lambda x: x.tag == 'domain_path', installationSettings)[0].text
    if not os.path.isdir(domainPath):
        return False

    global DOMAIN_PATH
    global USER_EMAIL
    global USER_TOKEN
    DOMAIN_PATH = domainPath
    if 'email' in [x.tag for x in installationSettings]:
        USER_EMAIL = filter(lambda x: x.tag == 'email', installationSettings)[0].text
    if 'token' in [x.tag for x in installationSettings]:
        USER_TOKEN = filter(lambda x: x.tag == 'token', installationSettings)[0].text
    return True

def query(qs, offline=False, format='/json'):

    assert not offline, "Error: Offline mode is not supported currently."

    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    params = urllib.urlencode({})
    conn = httplib.HTTPConnection(URL)
    conn.request("GET", format+qs, params, headers)
    response = conn.getresponse()

    data = json.loads(response.read())
    conn.close()

    return data

def simple_query(qs):
    res = query(qs)
    if res['error']:
        print "Error: %s" % res['message']
        return []
    else:
        return res['result']

def get_version():
    """Return the current API version"""
    return str(query('/version')['version'])

def get_collections(ipc = None):
    """Return the collections, optionally which are IPC or non-IPC"""
    res = query('/classical/collections/')
    if res['error']:
        print "Error: %s" % res['message']
        return []
    else:
        if ipc is not None:
            return filter(lambda x: x['ipc'] == ipc, res['result'])
        else:
            return res['result']

def get_collection(cid):
    """Return the collection of a given id"""
    return simple_query("/classical/collection/%d" % cid)

def find_collections(name):
    """Find the collections matching the string name"""
    return simple_query("/classical/collections/search?name=%s" % name)


def get_domains(cid):
    """Return the set of domains for a given collection id"""
    return simple_query("/classical/domains/%d" % cid)

def get_domain(did):
    """Return the domain for a given domain id"""
    return simple_query("/classical/domain/%d" % did)

def find_domains(name):
    """Return the domains matching the string name"""
    return simple_query("/classical/domains/search?name=%s" % name)


def get_problems(did):
    """Return the set of problems for a given domain id"""
    return map(localize, simple_query("/classical/problems/%d" % did))

def get_problem(pid):
    """Return the problem for a given problem id"""
    return localize(simple_query("/classical/problem/%d" % pid))

def find_problems(name):
    """Return the problems matching the string name"""
    return map(localize, simple_query("/classical/problems/search?problem_name=%s" % name))

def get_plan(pid):
    """Return the existing plan for a problem if it exists"""
    plan = simple_query("/classical/plan/%d" % pid)['plan'].strip()
    if plan:
        return map(str, plan.split('|'))
    else:
        return None


def localize(prob):
    """Convert the relative paths to local ones"""
    if not DOMAIN_PATH:
        return prob

    toRet = {k:prob[k] for k in prob}

    toRet['domain_path'] = os.path.join(DOMAIN_PATH, prob['domain_path'])
    toRet['problem_path'] = os.path.join(DOMAIN_PATH, prob['problem_path'])

    return toRet


if not checkForDomainPath():
    print "\n Warning: No domain path is set\n"

try:
    if VERSION != get_version():
        print "\n Warning: Script version doesn't match API. Do you have the latest version of this file?\n"
except:
    pass
