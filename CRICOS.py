import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import lxml
import csv
import time
import random

start_url = 'https://cricos.education.gov.au/Course/CourseDetails.aspx?CourseId='
count = 0  # count the number of urls

# set up the csv file to write into
with open('CRICOS_output_loc6.csv', 'w', newline='', encoding='utf-8') as f1:
    fieldnames = ['url', 'Provider', 'Course Name', 'Course Sector', 'CRICOS Course Code', 'VET National Code',
                  'Dual Qualification',
                  'Broad Field', 'Narrow Field', 'Detailed Field', 'Course Level', 'Foundation Studies',
                  'Work Component', 'Course Language', 'Duration (Weeks)', 'Tuition Fee', 'Non Tuition Fee',
                  'Estimated Total Course Cost', 'Work Component Total Hours', 'Work Component Hours/Week',
                  'Work Component Weeks', 'Course Locations', 'State']
    writer1 = csv.DictWriter(f1, fieldnames=fieldnames)
    # write column names in csv
    column_name = {}
    for name in fieldnames:
        column_name[name] = name
    writer1.writerow(column_name)

    # loop
    x = 59871
    while x < 103000:
        count = count + 1
        url = start_url + str(x)  # construct the url
        try:
            r = requests.get(url)  # get page source
        except:
            print('error happens')
            x = x
            time.sleep(15)
            continue
        x = x + 1   # need to put back
        s = bs(r.content, 'lxml')
        print("scraping ===" + str(count) + '===' + str(x) + "===" + url)

        # find page header <h1>
        Page_header = s.find_all('h1')[0]  # Page header is the first h1 in the page source
        Page_header_text = Page_header.string.strip()

        # if page deader is 'course search', skip to the next url
        if Page_header_text == 'Course Search':
            print('Invalid course code')
            continue
        else:

            results = {'url': url, 'Provider': Page_header_text}
            # scraping the content
            form = s.find(class_='form-horizontal')
            # print(form)
            box = form.find_all(class_='form-group display')
            # print(len(box))
            for div in box:
                label = div.find_all(class_='col-sm-12 col-md-3')
                if len(label):
                    key = label[0].string.replace(':', '')
                    # fieldnames.append(key)
                    # print(label[0].string)
                for row in div.find_all(class_='col-sm-12 col-md-9'):
                    span = row.select('span')
                    value = span[0].string
                    results[key] = value
                    # print(span)
                    # print(span[0].string)

            # find the locations offering a course

            # check if more than 10 locations
            if s.find(class_='gridPager'):   # to check if a pagegrid exists on the page
                browser = webdriver.Chrome()  # if more then 10 pages, use selenium to scrape
                browser.get(url)
                time.sleep(3)
                # location_table = browser.find_element_by_xpath('//*[@id="ctl00_cphDefaultPage_courseLocationList_gridSearchResults"]/tbody')
                # print(location_table)
                course_location = browser.find_element_by_xpath('//*[@id="tabCourseDetails"]/li[2]/a')   # find the course location tab
                course_location.click();   # click the course location tab
                time.sleep(1);

                page_no = browser.find_elements_by_xpath(
                    '//*[@id="ctl00_cphDefaultPage_courseLocationList_gridSearchResults"]/tbody/tr[@class="gridPager"]/td/table/tbody/tr/td')
                print(len(page_no))

                for i in range(len(page_no)):
                    soup = bs(browser.page_source, "html.parser")
                    location_form = soup.find(summary="This table shows the locations offering this course.")
                    for tr in location_form.find_all('tr')[1:-2]:
                        location = tr.find_all('span')[0].string
                        results['Course Locations'] = location  # update the dic results to add course locations
                        results['State'] = location[:3].strip()
                        writer1.writerow(results)
                    # button = page.find_element_by_xpath('//*[@id="ctl00_cphDefaultPage_courseLocationList_gridSearchResults"]/tbody/tr[@class="gridPager"]/td/table/tbody/tr/td[2]/a')
                    try:
                        button = browser.find_element_by_xpath(
                            '//*[@id="ctl00_cphDefaultPage_courseLocationList_gridSearchResults"]/tbody/tr[@class="gridPager"]/td/table/tbody/tr/td[{}]/a'.format(
                                i + 2))
                        button.click()
                        time.sleep(1)
                    except:
                        print('ok, no more pages')

                browser.close()
            else:
                try:
                    location_form = s.find(summary="This table shows the locations offering this course.")
                    for tr in location_form.find_all('tr')[1:]:
                        try:
                            location = tr.find_all('span')[0].string
                        except:
                            print('Cannot find span in location form')
                        results['Course Locations'] = location  # update the dic results to add course locations
                        results['State'] = location[:3].strip()
                        writer1.writerow(results)
                        print(results)
                except:
                    print('no course location')
                    print(results)
                    continue
