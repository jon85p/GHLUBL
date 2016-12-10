#!/usr/bin/env python3

import requests
import sys
import optparse
import os
import csv

def find_between( s, first, last , starting=0):
    try:
        start = s.index( first , starting) + len( first )
        end = s.index( last, start )
        return s[start:end], start
    except ValueError:
        return ""

def find_pages(s):
    '''
    Return search pages results
    '''
    last = s.index('</a> <a class="next_page"')
    start = last
    counter = 1
    while start != '>':
        start = s[last - counter]
        counter+=1
    return int(s[last + 2 - counter:last])

def find_users(htmls):
    '''
    Retrieve string users from each result html page
    '''
    users = []
    first = '<div class="user-list-info">\n    <a href="/'
    last = '">'
    for html in htmls:
        s = html
        start = 0
        temp = 'something'
        while temp != '':
            temp = find_between(s, first, last, start)
            if len(temp) == 2:
                user, start = temp[0], temp[1] + 1
                users.append(user)
    return users

def main():
    parser = optparse.OptionParser(sys.argv[0] + ' -c city -o output')
    parser.add_option('-c', dest='coption', type='string', \
    help='City for search')
    parser.add_option('-o', dest='ooption', type='string', \
    help='Output file in .csv format')
    (options, args) = parser.parse_args()
    if options.coption == None:
        print(parser.usage)
        exit(0)
    else:
        city = options.coption

    if options.ooption == None:
        output_filename = 'output.csv'
    else:
        output_filename = options.ooption
    direction = 'https://github.com/search?q=' + city.replace(' ', '+') +\
    '&type=Users&utf8=%E2%9C%93'
    r = requests.get(direction)
    first_page = r.text
    try:
        number_results = find_pages(first_page)
    except ValueError:
        number_results = 1
    print(str(number_results), 'pages found')
    print('Gathering pages info...')
    urls = []
    for i in range(number_results):
        link = 'https://github.com/search?p=' + str(i+1) + '&q=' + \
        city.replace(' ', '+') + '&type=Users&utf8=%E2%9C%93'
        urls.append(link)
    #Save html found pages
    htmls = []
    for i, url in enumerate(urls):
        r = requests.get(url)
        print(str(i+1), '/', str(number_results), sep='')
        htmls.append(r.text)
    #String users
    users = find_users(htmls)
    if len(users) == 0:
        print('No results found, exit...')
        exit(0)
    print('Looking info for each user...')
    dict_list = []
    for cont, user in enumerate(users):
        r = requests.get('https://api.github.com/users/' + user)
        dicc = r.json()
        print(str(cont + 1), '/', str(len(users)), sep='')
        dict_list.append(dicc)
    print('Saving csv file', output_filename)
    saving_success = False
    while saving_success == False:
        try:
            with open(output_filename, 'w') as f:
                w = csv.DictWriter(f, dict_list[0].keys())
                w.writeheader()
                for dic in dict_list:
                    w.writerow(dic)
            saving_success == True
        except:
            print('Error saving file, choose other file name')
            output_filename = input('>> ')
if __name__ == '__main__':
    main()
