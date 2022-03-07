# Press the green button in the gutter to run the script.


# Import libraries
import PyPDF2
import requests
from bs4 import BeautifulSoup

import tabula
import tempfile
import urllib
import io
import re
import sqlite3
from sqlite3 import Error
import datetime
from datetime import date

fp = tempfile.TemporaryFile()
from tabula import read_pdf
import warnings

warnings.filterwarnings('ignore')

# URL from which pdfs to be downloaded
url = "https://www.normanok.gov/public-safety/police-department/crime-prevention-data/department-activity-reports"

# Requests URL and get response object
response = requests.get(url)

# Parse text obtained
soup = BeautifulSoup(response.text, 'html.parser')

# Find all hyperlinks present on webpage
links = soup.find_all('a')

i = 0
alldate = []
allincidentnumber = []
allnature = []
alllocation = []
alldistincts = []
allincidentorl = []


def downloadfile():
    i = 0
    for link in links:
        if (('_incident_summary.pdf' in link.get('href', []))):
            i += 1
            print("Downloading file: ", i)
            print("the file is :", link.fi)

            # Get response object for link
            response = requests.get(link.get('href'))

            # Write content in pdf file
            pdf = open("pdf" + str(i) + ".pdf", 'wb')
            pdf.write(response.content)

            pdf.close()
            print("File ", i, " downloaded")

    print("All PDF files downloaded")


def status():
    con = sqlite3.connect("lastdb.db")
    # let's us execute commands in a database
    cur = con.cursor()
    for row in cur.execute('''SELECT DISTINCT(nature) FROM lastdb '''):
        alldistincts.append(row)
    for val in alldistincts:
        value = cur.execute('''SELECT COUNT(*) from lastdb WHERE nature = ? ''', val)
        ans = cur.fetchone()
        print(fr'{val} | {ans}')


def completeextractdata():
    url = ("https://www.normanok.gov/sites/default/files/documents/"
           "2022-02/2022-02-21_daily_incident_summary.pdf")

    headers = {}
    headers[
        'User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"

    data = urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read()
    # df = read_pdf("pdf20.pdf",pages="1")
    # Write the pdf data to a temp file
    fp.write(data)

    # Set the curser of the file back to the begining
    fp.seek(0)

    # Read the PDF
    pdfReader = PyPDF2.pdf.PdfFileReader(fp)
    pagecount = pdfReader.getNumPages()
    for iv in range(0,pagecount):


        # Get the first page
        page1 = pdfReader.getPage(iv).extractText()
        count = 0
        for line in io.StringIO(page1):
            if (count == 0):
                datevalue = "Null"
                datev = re.search(r'(\d+/\d+/\d+ \d+\:\d+)', line)

                if (datev != None):
                    datevalue = datev.group(1)
                alldate.append(datevalue)

               # print("line is", line)
               # print("date is ", datevalue)

                pass

            if (count == 1):
                inc = "Null"
                incnumber = re.search(r'(\d{4}-\d+)',line)
                if(incnumber != None):
                    inc = incnumber.group(1)
                allincidentnumber.append(inc)
                #print("incidentnumber is ",inc)

                pass
            if (count == 2):
                loc = "Null"
                locvalue = re.findall(r'([A-Z0-9]+)',line)
                if(locvalue != None):
                    if(len(locvalue)>2):
                        loc = line
                alllocation.append(loc)
                #print("location number is",loc)
                pass

            if (count == 3):
                nat = "Null"
                natvalue = re.search(r'(?<!\.)\s+([A-Z][a-z]+(?<!\/)+)',line)
                if((natvalue != None)):
                    nat = line
                allnature.append(nat)
                #print("nature number is",nat)
                pass

            if (count == 4):
                inc = "Null"
                incvalue = re.search(r"(?<![^\s,])[A-Z]+[0-9]+(?![^\s,])",line)
                if(incvalue != None):
                    inc = line

                # count =0
                allincidentorl.append(line)
                print("incidentor number is",line)
                pass
            if (count > 3):

                count = 0
                pass
            else:
                count += 1
                pass

def printalldata():
    con = sqlite3.connect("lastdb.db")
    # let's us execute commands in a database
    cur = con.cursor()
    state = '''SELECT COUNT(*) FROM lastdb WHERE nature = ? '''

    for row in cur.execute('''SELECT * FROM lastdb '''):
        print(row)


def savetoDb():
    con = sqlite3.connect("lastdb.db")
    # let's us execute commands in a database
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS lastdb
    (dategiven text, incidentnumber text,nature text,location text ,incidentorurl text)
    ''')
    for va in range(0,
                    min(len(alldate), len(allnature), len(alllocation), len(allincidentorl), len(allincidentnumber))):
        cur.execute(
            '''INSERT INTO lastdb(dategiven,incidentnumber,nature,location,incidentorurl) VALUES(?,?,?,?,?)''',
            ( str(alldate[va]), str(allincidentnumber[va]), str(allnature[va]), str(alllocation[va]), str(allincidentorl[va])))

    con.commit()
    for row in cur.execute('''SELECT * FROM lastdb'''):
        print(row)


downloadfile()
completeextractdata()
savetoDb()
printalldata()
status()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
