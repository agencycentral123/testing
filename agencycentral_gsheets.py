#!/usr/bin/env python3

import json
import csv
import time
from bs4 import BeautifulSoup
import requests
from requests.structures import CaseInsensitiveDict
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account

def get_google_creds():
    SERVICE_ACCOUNT_FILE = 'keyszee.json'


    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = None
    credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)



    service = build('sheets', 'v4', credentials=credentials)


    sheet = service.spreadsheets()

    return sheet


def update_sheet(sheet, SPREADSHEET_ID, SHEET_RANGE, data):
    try:
        result = sheet.values().clear(spreadsheetId=SPREADSHEET_ID,
                                range=SHEET_RANGE,
                                body={}).execute()
    except Exception:
        pass

    result = sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                                range=SHEET_RANGE,
                                valueInputOption="USER_ENTERED",
                                body={"values":data}).execute()

def main2():
    CHROMEDRIVER_PATH = "/home/umut/.local/bin/chromedriver"
    driver = selenium_driver(CHROMEDRIVER_PATH)


    
    driver.get("https://www.totaljobs.com/browse-jobs")
    input("adsad1")

    
    driver.get("https://www.agencycentral.co.uk/agencysearch/search.htm?location=&do=search&order=covers&job_types%5B0%5D=contract&emp_cand=cnd&industry=accounting&skill=&location_id=&page=2")
    input("asdasd2")
    driver.get("")
    input("asdasd3")

    
def selenium_driver(CHROME_PATH):
    chrome_options = Options()
    
    PATH = CHROME_PATH
    s = Service(PATH)
    #chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_argument('--disable-browser-side-navigation')
    

    driver = webdriver.Chrome(service=s, options=chrome_options)
    driver.set_window_size(1920, 1080)
    
    
    return driver




















def get_data(tag):
    js_headers = ["type","name","address","location","town","county","post_code","country","streetmap_postcode","telephone","fax","email","employer_telephone","employer_fax","employer_email","approved","longitude","latitude","town_location_id","location_id","assisted_contact_telephone","full_postal_address","ac_county_code"]
    r = requests.get("https://www.agencycentral.co.uk/ajax/agencies/branches?tag="+tag)
    if r.status_code == 200:
        data = []
        js = r.json()
        r.close()
        js_key = js.keys()
        for key in js.keys():
            new_js = js[key]

        for head in js_headers:
            data.append(new_js[head])
        
        
        
        return data
        
        

def scrape_page(soup: BeautifulSoup()):
    divs = soup.select(".agency-result.row")
    total_arr = []
    for div in divs:
        data_tag = div["data-tag"]
        arr = get_data(data_tag)
        try:
            il = div["data-il"]
            if il:
                arr.append(il.replace(",,", ","))
        except Exception:
            pass

        try:
            about = div.select("p.about-agency")[0].text.strip("\n").strip(" ")
        except Exception:
            try:
                about = div.select("h2.agency-title")[0].text.strip("\n").strip(" ")
            except Exception:
                about = ""
        try:
            desc = div.select("p.agency-strapline-description")[0].text.strip("\n").strip(" ")
        except Exception:
            try:
                desc = div.select("div.agency-description")[0].text.strip("\n").strip(" ")
            except Exception:
                desc = ""
        try:
            inner_desc = div.select("div.agency-strapline > p > strong")[0].text.strip("\n").strip(" ")
        except Exception:
            inner_desc = ""
        try:
            recruitment_type = inner_desc.split("|")[1].strip("\n").strip(" ")
        except Exception:
            recruitment_type = ""
        try:
            category_name = inner_desc.split("|")[0].strip("\n").strip(" ")
        except Exception:
            category_name = ""
        


        cat_n = soup.select("p.search-successful-title > strong")[-1].text
        rec_t = "Contract, Temporary"

        arr.insert(0, desc)
        arr.insert(0, about)
        arr.insert(0, recruitment_type)
        arr.insert(0, category_name)

        arr.insert(0, rec_t)
        arr.insert(0, cat_n)
        total_arr.append(arr)
        
    return total_arr
    

def get_one_req2(category, csv_writer, numm):
    req_url = f"https://www.agencycentral.co.uk/agencysearch/search.htm?location=&do=search&order=covers&job_types[]=contract&job_types[]=temporary&emp_cand=cnd&industry={category}&skill=&location_id="
    r = requests.get(req_url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "lxml")
        cat_n = soup.select("p.search-successful-title > strong")[0].text.strip("\n").strip(" ")
        
        r.close()
        print(numm + int(cat_n))
        return numm + int(cat_n)

def get_one_req(category):
    req_url = f"https://www.agencycentral.co.uk/agencysearch/search.htm?location=&do=search&order=covers&job_types[]=contract&job_types[]=temporary&emp_cand=cnd&industry={category}&skill=&location_id="
    r = requests.get(req_url)
    cat_data = []
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "lxml")
        r.close()
        for ii in scrape_page(soup):
            cat_data.append(ii)
        page_count = 2

        while True:
            print("Page on "+str(page_count))
            last_li = soup.select("ul.paginator > li")[-1]
            if last_li.select("a"):
                r = requests.get(req_url+"&page="+str(page_count))
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, "lxml")
                    r.close()
                    for ii in scrape_page(soup):
                        cat_data.append(ii)
                    
                    page_count += 1
            else:
                break

    else:
        return []
    return cat_data


def main():
    SPREADSHEET_ID = "1AvV5Z-iqLHaa5WjFkXUoslL_1i_ZAl5fZymEC2OJxz0"
    SPREADSHEET_RANGE = "agencycentral!A2:AD"
    start = time.time()
    #cats = get_cats()
    cats = ["IT", "engineering", "socialcare"]
    cats = ["IT"]
    data = []
    try:
        for i, cat in enumerate(cats):
            for item in get_one_req(cat):
                data.append(item)
    except Exception as e:
        print(e)
    finally:
        # TODO change sheetIds
        print(data)
        print(len(data))
        sheet = get_google_creds()
        update_sheet(sheet, SPREADSHEET_ID, SPREADSHEET_RANGE, data)
        print(start - time.time())




def get_cats():
    ret_arr = []
    r = requests.get("https://www.agencycentral.co.uk/ajax/industry_modal")
    if r.status_code == 200:
        try:
            soup = BeautifulSoup(r.text, "lxml")
            r.close()
            lis = soup.select(".industry-choice.heading-span-link")
            for li in lis:
                strg = li["data-value"]
                if strg not in ret_arr:
                    ret_arr.append(strg)
            return ret_arr
        except Exception as e:
            print("Error: " + str(e))
    else:
        print("Categories couldn't fetch")
        return []




if __name__ == "__main__":
    main()
    