#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import urljoin
from urllib.parse import urlparse
import re
import requests
import pandas as pd
import io
import os


# In[ ]:


def get_HMD_codes():
    
    myLinks = []
    myLinksShort = []

    html_page = urllib.request.urlopen("https://mortality.org/Data/DataAvailability")
    soup = BeautifulSoup(html_page, "html.parser")
    for link in soup.findAll('a', attrs={'href': re.compile("=")}):
        myLinks.append(link.get("href"))
    for i in range(len(myLinks)):
        myLinksShort.append(myLinks[i].split("=")[1])
    out = [x.strip(' ') for x in myLinksShort]
    return out

def make_dir(the_path, data):

    for i in data:
        os.makedirs(os.path.join(the_path, i), exist_ok=True)


# In[ ]:


codes = get_HMD_codes()


# In[ ]:


data = []

while True:
    choice = input("Select your countries (type 'done' to make it stop). \n --> ")

    if choice == 'done':
        if len(data)!=0:
            break
        else:
            print("Please select at least one country.")                
                
    if choice in codes:
        data.append(choice)
    else:
        print("Please type in a valid country code (e.g., 'AUS' for Australia).")

print("You have selected: ", str(data)[1:-1])


# In[ ]:


data2 = []

while True:
    choice = input("Select a file such as 'Births.txt' or 'Deaths_1x1.txt' (type 'done' to make it stop). \n --> ")

    if choice == 'done':
        break            
                        
    data2.append(choice)
    
print("You have selected: ", str(data2)[1:-1])  


# In[ ]:


while True:
    loginurl = 'https://www.mortality.org/Account/Login'
    user_mail = input("Please enter your HMD username --> ")
    user_pw = input("Please enter your HMD password --> ")
    payload = {
    'ReturnUrl': 'https://www.mortality.org/Home/Index',
    'Email': str(user_mail),
    'Password': str(user_pw)
    }
    with requests.Session() as sess:
        res = sess.get(loginurl)
        signin = BeautifulSoup(res._content, 'html.parser')
        the_tok = signin.find('input', {'name': '__RequestVerificationToken'})['value']
        payload['__RequestVerificationToken'] = the_tok
        r = sess.post(loginurl, data = payload)
        dat = sess.get('https://www.mortality.org/File/GetDocument/hmd.v6/AUS/STATS/Births.txt', allow_redirects=False)
        if dat.status_code == 200:
            break
        else:
            print("Username or password incorrect")


# In[ ]:


while True:        
    my_path = input("Please type in the path (e.g., 'C:/HMDdata/') --> ")        
    if os.path.exists(my_path):
        break
    else:
        print("The folder does not exist")

make_dir(the_path = my_path, data=data)


# In[ ]:


url_start = "https://www.mortality.org/File/GetDocument/hmd.v6/"
for i in data:
    
    for j in data2:
        file_name = os.path.join(my_path, i)
        final_name = os.path.normpath(os.path.join(file_name,j))
        the_link = url_start+i
        final_link = the_link+"/STATS/"+j
        
        with requests.Session() as sess:
            res = sess.get(loginurl)
            signin = BeautifulSoup(res._content, 'html.parser')
            the_tok = signin.find('input', {'name': '__RequestVerificationToken'})['value']
            payload['__RequestVerificationToken'] = the_tok
            r = sess.post(loginurl, data = payload)
            dat = sess.get(final_link, allow_redirects=False)
            if dat.status_code != 200:
                print("Something went wrong. Maybe a typo in the file name?\n", final_link)
                continue
            else:
                open(final_name, 'wb').write(dat.content)
                print("Written file:\n", final_name)

