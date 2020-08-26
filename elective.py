from lxml import html
from bs4 import BeautifulSoup
from collections import namedtuple
import urllib.request
import requests
import json
import re
import ssl

def get_elective_course():
    #paths=get_courses_websites()
    paths=get_posibile_coure_web()
    for p in paths:
        find_elective_course(p)

def get_posibile_coure_web():
    course_codes = open("/Desktop/elective/selected_course_code.txt")
    course_line = course_codes.readline()
    course_lst=[]
    while course_line:
        course_lst.append(course_line.replace('\n', ''))
        course_line = course_codes.readline()
    course_codes.close()

    f = open("/Desktop/elective/could.txt")
    line = f.readline()
    lst=[]
    while line:
        lst.append(str(line.replace('\n', '')))
        line = f.readline()
    f.close()

    res=[]

    for i in lst:
        page=requests.Session().get(i) 
        tree=html.fromstring(page.text) 
        result=tree.xpath('//div[@id="page-title-area"]//h1/text()')

        result=str(result)
        if result in course_lst:
            res.append(i)
    return res

def get_courses_websites():
    f = open("/Desktop/elective/course.txt")
    line = f.readline()
    lst=[]
    while line:
        lst.append(line)
        line = f.readline()
    f.close()

    res=[]

    pattern = re.compile('/en/courses/\w\w\w/')
    for l in lst:
        find = re.findall(pattern, l)
        for f in find:
            res.append("https://catalogue.uottawa.ca"+f)
            
    return res


def cleanFrench9(content):
    content = content.replace(" /", "%%&&",1)
    pattern = re.compile(r'(%%&&)([\s\S]*)(%%&&)')
    return pattern.sub(r'', content)

#https://catalogue.uottawa.ca/en/courses/mat/
def find_elective_course(path):
    context = ssl._create_unverified_context()
    htmlfile = urllib.request.urlopen(path,context=context).read().decode('utf-8')

    soup = BeautifulSoup(htmlfile, features='lxml')
    courseblocks = soup.find_all('div', attrs={'class': 'courseblock'})
    
    french_line = '/'
   

    taken =['ITI1120', 'MAT1320', 'MAT1341', 'ITI1100', 'ITI1121', 'MAT1322', 'MAT1348', 'CEG2136', 'CSI2110', 'ENG1112', 'SEG2105',
            'CSI2101', 'CSI2120', 'CSI2132', 'MAT2377', 'CSI2911', 'CSI3105', 'CSI3120', 'CSI3130', 'CSI3104', 'CSI3131', 'CSI3140',
            'CEG3185', 'CSI4106', 'CSI4107']

    
    elective=[]

    Document = namedtuple("Document", "Course Description Prerequisites")

    for courseblock in courseblocks:
        course_title = courseblock.find('p', attrs={'class': 'courseblocktitle'}).text

        eng_course_pattern = re.compile('[A-Za-z][A-Za-z][A-Za-z]\s[1-4][1-4|0|9]\d\d')
        
        course_code = re.findall(eng_course_pattern,course_title)
        course_code = ["".join(c.split()) for c in course_code]


        tmp_course_pattern = re.compile('[A-Za-z][A-Za-z][A-Za-z]\s\d\d\d\d')
        
        tmp_course_code = re.findall(tmp_course_pattern,course_title)
        tmp_course_code = ["".join(c.split()) for c in tmp_course_code]
        
        #print(course_title)
        #for c in course_code:

        if tmp_course_code[0] in taken:
            pass
        elif re.search("Work Term",course_title):
            pass
        elif re.match("^[A-Za-z][A-Za-z][A-Za-z]\s[1-4][1-4]",course_title):
            extra=courseblock.find('p',attrs={'class': 'courseblockextra highlight noindent'})
            if extra is None:
                course_description = courseblock.find('p', attrs={'class': 'courseblockdesc'})
                new_document = Document(re.sub('\(.*?\)', '', course_title),course_description.text.strip() if course_description is not None else '','')
                elective.append(new_document)
            else:
                #prequisites
                #Permission of the Department is required.
                if ('prerequisite' in extra.text.lower().strip()) or ('corequisite' in extra.text.lower().strip()) or ('previously' in extra.text.lower().strip()) or ('prerequisites' in extra.text.lower().strip()) or ('prerequiste' in extra.text.lower().strip()) or ('prerequistes' in extra.text.lower().strip()) or ('préalables' in extra.text.lower().strip()) or ('préalable' in extra.text.lower().strip()):
                    pre_courses=re.findall(eng_course_pattern,extra.text.strip())
                    pre_courses=["".join(p.split()) for p in pre_courses]
                    for tmp in pre_courses:
                        if "".join(tmp.split()) in taken:
                            course_description = courseblock.find('p', attrs={'class': 'courseblockdesc'})
                            new_document = Document(re.sub('\(.*?\)', '', course_title),course_description.text.strip() if course_description is not None else '',extra.text.strip())
                            elective.append(new_document)
                            break
                else:
                    course_description = courseblock.find('p', attrs={'class': 'courseblockdesc'})
                    new_document = Document(re.sub('\(.*?\)', '', course_title),course_description.text.strip() if course_description is not None else '',extra.text.strip())
                    elective.append(new_document)

        elif re.match("^[A-Za-z][A-Za-z][A-Za-z]\s[1-4][9｜0]",course_title):
            tmp = list(course_title)
            tmp.insert(9, '%%&& ')
            course_title = ''.join(tmp)
            course_title=cleanFrench9(course_title)
            course_description = courseblock.find('p', attrs={'class': 'courseblockdesc'})
            
            if course_description is not None:
                course_description = course_description.text.strip()
                if french_line in course_description:
                    tmp = list(course_description)
                    tmp.insert(0, '%%&& ')
                    course_description = ''.join(tmp)
                    course_description = cleanFrench9(course_description)
            else:
                course_description=''

            extra=courseblock.find('p',attrs={'class': 'courseblockextra highlight noindent'})

            if extra is not None:
                extra = extra.text.strip()
                if french_line in extra:
                    tmp = list(extra)
                    tmp.insert(0, '%%&& ')
                    extra = ''.join(tmp)
                    extra = cleanFrench9(extra)

                if ('previously' in extra.lower()) or ('corequisite' in extra.lower())  or('prerequisite' in extra.lower()) or ('prerequisites' in extra.lower()) or ('prerequiste' in extra.lower()) or ('prerequistes' in extra.lower()) or ('préalables' in extra.lower()) or ('préalable' in extra.lower()):
                    pre_courses=re.findall(eng_course_pattern,extra)
                    pre_courses=["".join(p.split()) for p in pre_courses]
                    
                    for tmp in pre_courses:
                        if "".join(tmp.split()) in taken:
                            new_document = Document(re.sub('\(.*?\)', '', course_title),course_description,extra)
                            elective.append(new_document)
                            break
                else:
                    new_document = Document(re.sub('\(.*?\)', '', course_title),course_description,extra)
                    elective.append(new_document)

            else:
                new_document = Document(re.sub('\(.*?\)', '', course_title),course_description,'')
                elective.append(new_document)


    electives = [e._asdict() for e in elective]

    if electives !=[]:
        print(path)

    with open('selected_electives_courses.json', 'a') as outfile:
        json.dump(electives, outfile, ensure_ascii=False, indent=4)
