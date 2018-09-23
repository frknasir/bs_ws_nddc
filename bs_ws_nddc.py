#import libraries
from bs4 import BeautifulSoup
import requests
import csv

#function to scrape an individual page
def scrapePage(soup):
    data = []

    #find projects within the table
    projects = soup.find_all(
        'div', 
        attrs={'style':'border-bottom: dotted 1px #ddd; padding-bottom: 10px; margin-bottom: 15px'}
    )

    #loop over projects
    for project in projects: 
        meta = project.select('span strong')

        #write to variables
        state = meta[0].getText()
        lg = meta[1].getText()
        status = meta[2].getText()
        category = meta[3].getText()
        title = project.find('a', attrs={'class': 'lplnk'})

        #scrape from project's details page
        detailsLink = title.get('href').split(',')
        link = detailsLink[4].replace('"', '').strip(' ')
        result = requests.get('http://nddcproject.nddc.gov.ng/'+link, timeout=5)
        s = BeautifulSoup(result.content, 'lxml')
        details = s.find_all('div', attrs={'class': 'col-md-7 col-sm-7 col-xs-7'})
        award_date = details[2].getText()
        contractor = details[4].getText()

        data.append([title.getText(), state, lg, status, category, award_date, contractor])
        #print(award_date + ' ' + contractor)

    return data

#function to return the next page button
def checkPagination(soup):
    pagination = soup.find(
        'input', 
        attrs={'type':'image', 'src': 'App_Themes/img/next.gif'}).get('onclick')
    pagination = pagination.replace('javascript:__doPostBack(', '')
    pagination = pagination.replace(');return false;', '')
    pagination = pagination.replace("'", '')
    pagination = pagination.split(',')

    return pagination

#declaration of the initial parameters
urlpage =  'the url of the first page of the projects you are trying to scrape'
file_title = 'name_of_the_to_save_results_to.csv'
hasNext = True
pagination = []
count = 1

#create and write headers to a list
rows = []
rows.append(
    [
        'Title',
        'State', 
        'LGA', 
        'Status', 
        'Category', 
        'Award Date', 
        'Contractor'
    ]
)

# query the website and return the html to the variable 'page'
try:
    page = requests.get(urlpage, timeout=5)
except:
    print("Something went wrong")
    exit()

# parse the html using beautiful soup and store in variable 'soup'
soup = BeautifulSoup(page.content, 'lxml')

#add scraped data from the first page 
d = scrapePage(soup)
for val in d:
    rows.append([
        val[0],
        val[1],
        val[2],
        val[3],
        val[4],
        val[5],
        val[6]
    ])
print("page ",count, " scraped successfully")

try:
    #find pagination links
    pagination = checkPagination(soup)
except: 
    hasNext = False
    print("probably the end...we could be wrong tho!")
    
while(hasNext) :

    eventTarget = pagination[0]
    eventArgument = pagination[1]
    viewState = soup.find('input', attrs={'id':'__VIEWSTATE'}).get('value')

    #try a paginated request
    r = requests.post(
        urlpage,
        data = {
            '__EVENTTARGET': eventTarget,
            '__EVENTARGUMENT': eventArgument,
            '__VIEWSTATE': viewState
        }
    )

    soup = BeautifulSoup(r.content, 'lxml')
    d = scrapePage(soup)
    for val in d:
        rows.append([
            val[0],
            val[1],
            val[2],
            val[3],
            val[4],
            val[5],
            val[6]
        ])
    count = count + 1
    print("page ",count, " scraped successfully")

    try:
        #find pagination links
        pagination = checkPagination(soup)
    except: 
        hasNext = False
        print("scraped data written to the file: ", file_title)

# Create csv and write rows to output file
with open(file_title,'w', newline='') as f_output:
    csv_output = csv.writer(f_output)
    csv_output.writerows(rows)
