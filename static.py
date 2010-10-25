#!/usr/bin/env python

import sys, csv, xlrd, os, shutil, commands, re, socket, time, getpass
import urllib, urllib2, cookielib, MultipartPostHandler, httplib
from BeautifulSoup import BeautifulSoup

url = 'https://tools.varolii.com/'

def main():
    if len(sys.argv) <= 2:
        print 'You must pass in two filenames.  First one is the Prompt Sheet xls, second one is the output zip file.'
        print 'eg. ./static.py voice_prompts.xls voice_prompts.zip'
        sys.exit(1)
    else:
        listdata = readfile(sys.argv[1])
        zipfile =  sys.argv[2]
        controlfile()
        filestozip = getfiles()
        zip(filestozip, zipfile)
        opener = authenticate()
        upload(opener, zipfile)

def readfile(filename):
    '''Reads xls file passed in and writes out to prompts.csv.'''
    writer = csv.writer(open('prompts.csv', 'wb'))
    book = xlrd.open_workbook(filename) 
    sh = book.sheet_by_index(0) 
    for rx in range(sh.nrows):
        writer.writerow((sh.row_values(rx)))
        
     
def controlfile():
    '''Writes out a text file that handle how the prompts should be processed and with which voice talent.'''

       
    talents = {'Leslie' : 'F_ENG_4\n',
               'Krisha' : 'F_ENG_5\n',
               'Jen' : 'F_ENG_6\n',
               'Sneha' : 'F_ENG_7\n',
                'Maru' : 'F_ESP_4\n',
               'Dave' : 'M_ENG_4\n',
               'Fabio' : 'M_ESP_3\n',
}
    
    print "Voice Talents"
    print "============================================="
    for k, v in talents.items():
        print(k)
    try:
        talent = raw_input('Please select a voice talent: ')
        file = open('control.txt', 'wb')
        file.write('vocab = ' + talents[talent])
        file.write('plural = N\n')
        file.write('type = STATIC\n')
        file.close
    except (KeyError):
        print "Voice Talent does not exist.\n"
        main()
    except (KeyboardInterrupt):
        print "Keyboard Interrupt. Exiting."
        sys.exit(1)
        

def getfiles():
    '''Gets list of pcm files'''
    result = []
    paths = os.listdir(os.curdir)  # list of paths in that dir
    for fname in paths:
        match = re.search(r'.pcm', fname)
        if match:
            result.append(os.path.abspath(os.path.join(os.curdir, fname)))
    return result

    
def zip(paths, zipfile):
  """Zip up all of the given files into a new zip file with the given name."""
  cmd = 'zip -j ' + zipfile + ' ' + 'prompts.csv' + ' ' +  ' ' + 'control.txt' + ' ' + ' '.join(paths) 
  #print "Command I'm going to do: " + cmd
  print '========================================='
  print 'Zipping up the following files: '
  print 'prompts.csv'
  print 'control.txt'
  for path in paths:
    print path
  (status, output) = commands.getstatusoutput(cmd)
  # If command had a problem (status is non-zero),
  # print its output to stderr and exit.
  if status:
    sys.stderr.write(output)
    sys.exit(1)
    
def authenticate():
    username = raw_input('Please enter Username: ')
    password = getpass.getpass('Please enter Password: ')
    cj = cookielib.CookieJar()
    ck = cookielib.Cookie(version=0, name='killmenothing', value='', port=None, port_specified=False, domain='tools.varolii.com', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
    cj.set_cookie(ck)
    

    opener = urllib2.build_opener(MultipartPostHandler.MultipartPostHandler, urllib2.HTTPCookieProcessor(cj))
    login_data = urllib.urlencode({'frmUserID' : username, 'frmPassword' : password, 'formAction' : 'login'})
    opener.open(url + 'admin_login_page.jsp')
    resp = opener.open(url + 'AdminLoginServlet', login_data)
    result = resp.read()
    match = (re.search(r'escape\(".*"\)', result))
    if match is not None:
        validmatch = match.group()
    else:
        print "Login Failed. Exiting."
        sys.exit(1)
    sessiontoken = validmatch[8:40]
    
    resp = opener.open(url + 'change_role_db.jsp?roleNum=2&GlobalSessionToken=' + sessiontoken)
    
    result = resp.read()
    
    soup = BeautifulSoup(result)
    clientlist_dict = {}
    table = soup.find("select", {"name" : "ahClientList"})
    for row in table.findChildren('option')[1:]:
        clientlist_dict[row.get('value')] = row
    for k, v in clientlist_dict.items():
        clients = '%s, %s' % (k, v.contents)
        print clients
    selectclient = raw_input('Please enter a client number: ')
    client = selectclient
    if client not in clientlist_dict.keys():
        print 'You must enter a client ID. Exiting.'
        sys.exit(1)
    else:
        opener.open(url + 'change_client_db.jsp?clientNum=' + client + '&GlobalSessionToken=' + sessiontoken)
    return opener
   
def upload(opener, zipfile):
    uploadparams = {'uploadFileName':open(zipfile, 'rb')}
    urllib2.install_opener(opener)
    req = urllib2.Request(url + 'VoicePromptBatchUploadServlet', uploadparams)
    urllib2.urlopen(req).read().strip()
    results = urllib2.urlopen(url + 'voice_batch_upload_viewer.jsp')
    uploadresult = results.read()
    print uploadresult
    time.sleep(20)
    results = urllib2.urlopen(url + 'voice_batch_upload_viewer.jsp')
    uploadresult = results.read()
    print uploadresult


if __name__ == '__main__':
    main()