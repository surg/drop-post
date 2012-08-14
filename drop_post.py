#! /usr/bin/env python
import getpass
import base64
import httplib
import urllib
import json
import getopt
import sys
from drop_post_config import Config

def usage():
    print """%s file --title title [--private | --autopost | --tags 'comma_separated_tags']""" % sys.argv[0]

def get_basic_authorization_hash():
    user = raw_input('Email: ')
    password = getpass.getpass('Password: ')
    auth_string = base64.b64encode(user + ':' + password)
    return auth_string

def publish_post(title, filename, tags=None, is_private=False, autopost=False):
    """
    Function used to post things to posterous. First try.
    """
    auth_string = Config.auth_string
    token = Config.token

    conn = httplib.HTTPConnection('posterous.com')
    headers = { 'Authorization': 'Basic ' + auth_string }

    try:
        content = open(filename, 'r').read()
        content = '<markdown>' + content + '</markdown>'
    except IOError:
        print "Error opening file {0}.".format(filename)
        sys.exit(2)

    print 'Trying to post...'
    params = {
        'api_token': token,
        'post[title]': title,
        'post[body]': content,
        'post[is_private]': is_private,
        'post[autopost]': autopost
    }
    if tags:
        params.update({'post[tags]': tags})
    params = urllib.urlencode(params)
    headers.update({"Content-type": "application/x-www-form-urlencoded"})
    url = '/api/2/sites/%s/posts' % Config.site_id
    conn.request('POST', url, params, headers)
    res = conn.getresponse()
    res_body = res.read()
    data = json.loads(res_body)
        
    if "full_url" in data:
        print "Check it out your new post at ", data['full_url']
    else:
        print "Failed: "
    print json.dumps(data, indent = 2)    

if __name__ == "__main__":
    autopost = False
    is_private = False
    tags = None
    opts, args = getopt.getopt(sys.argv[1:], "t:", [
        'title=', 'tags=', 'autopost', 'private'])
    for k, v in opts:
        if k == '-t' or k == '--title':
            title = v
        elif k == '--tags':
            tags = v
        elif k == '--autopost':
            autopost = True
        elif k == '--private':
            is_private = True
    if not args:
        usage()
        sys.exit(2)
    else:
        filename = args[0]
    publish_post(title, filename, tags, is_private, autopost)