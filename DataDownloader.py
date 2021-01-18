from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import datetime
from tqdm import tqdm
import sqlite3
import os.path
import shutil

class downloader:

    def __init__(self):
        chop = webdriver.ChromeOptions()
        chop.add_extension('Adblock Plus - darmowy adblocker.crx')
        self.__driver = webdriver.Chrome(chrome_options=chop)

    def close_tab(self):
        self.__driver.quit()

    def download_average_fuel_values(self, url):
        data_container = [None, None, None, None]

        driver = self.__driver
        driver.get(url)

        table = driver.find_element_by_xpath("//div[@class='fuels-wrapper choose-petrol']")
        fuels = table.find_elements_by_xpath(".//a")

        for i in fuels:
            if i.find_element_by_xpath(".//h3").text == "95":
                data_container[0] = i.find_element_by_xpath(".//div").text
            if i.find_element_by_xpath(".//h3").text == "98":
                data_container[1] = i.find_element_by_xpath(".//div").text
            if i.find_element_by_xpath(".//h3").text == "ON":
                data_container[2] = i.find_element_by_xpath(".//div").text
            if i.find_element_by_xpath(".//h3").text == "LPG":
                data_container[3] = i.find_element_by_xpath(".//div").text

        return data_container

    def download_fuel_values(self, url):
        data_container = []

        driver = self.__driver
        driver.get(url)

        try:
            driver.find_element_by_xpath("//button[@onclick]").click()
        except:
            print("NO COOKIES FOUND TO ACCEPT")

        while(True):
            time.sleep(3)

            table = driver.find_element_by_xpath("//table[@id='price_table']").find_element_by_xpath(".//tbody")
            table = table.find_elements_by_xpath(".//tr")

            for station in tqdm(table):
                adress = station.find_elements_by_xpath(".//td")[0].text.replace('\n', ' ')
                PriceAndDate = station.find_elements_by_xpath(".//td")[1].text.split('\n')

                if len(PriceAndDate)==1:
                    continue

                price = PriceAndDate[0]
                date = PriceAndDate[1]

                data_container.append([adress, price, date])

            next_button = driver.find_element_by_xpath("//li//a[contains(text(), '>')]")
            if next_button.find_element_by_xpath('..').get_attribute('class') == 'disabled':
                break
            next_button.click()

        return data_container

    @staticmethod
    def create_database():
        #MOVE OLD FILE IF IT EXISTS
        if os.path.exists("prices.db"):
            dir_name ="old_files/"+str(datetime.date.today())
            if not os.path.exists(dir_name):
                os.mkdir(dir_name)
            shutil.move("prices.db", dir_name+"/prices.db")

        #CREATE DATABASE
        conn = sqlite3.connect("prices.db")
        c = conn.cursor()

        #CREATE TABLE STATIONS
        c.execute('''CREATE TABLE STATIONS
                        ([station_id] INTEGER PRIMARY KEY, [adress] text);''')

        #CREATE TABLE PRICES ON
        c.execute('''CREATE TABLE PRICE_ON
                    (
                    [station_id] integer, [price] text, [date] text,
                    FOREIGN KEY (station_id) REFERENCES STATIONS (station_id)
                    );''')

        # CREATE TABLE PRICES E95
        c.execute('''CREATE TABLE PRICE_E95
                    (
                    [station_id] integer, [price] text, [date] text,
                    FOREIGN KEY (station_id) REFERENCES STATIONS (station_id)
                    );''')

        # CREATE TABLE PRICES E98
        c.execute('''CREATE TABLE PRICE_E98
                    (
                    [station_id] integer, [price] text, [date] text,
                    FOREIGN KEY (station_id) REFERENCES STATIONS (station_id)
                    );''')

        # CREATE TABLE PRICES LPG
        c.execute('''CREATE TABLE PRICE_LPG
                    (
                    [station_id] integer, [price] text, [date] text,
                    FOREIGN KEY (station_id) REFERENCES STATIONS (station_id)
                    );''')

        # CREATE TABLE AVERAGE PRICES
        c.execute('''CREATE TABLE AVG_PRICES
                    (
                    [fuel] text, [price] text
                    );''')

        conn.commit()
        conn.close()

    @staticmethod
    def merge_data(data_e95, data_e98, data_on, data_lpg):
        merged_data = [[], []]

        for i in data_e95:
            merged_data[0].append(i[0])
            merged_data[1].append([[i[1], i[2]], [None, None], [None, None], [None, None]])

        for i in data_e98:
            if i[0] in merged_data[0]:
                merged_data[1][merged_data[0].index(i[0])][1][0] = i[1]
                merged_data[1][merged_data[0].index(i[0])][1][1] = i[2]
            else:
                print(i)

        for i in data_on:
            if i[0] in merged_data[0]:
                merged_data[1][merged_data[0].index(i[0])][2][0] = i[1]
                merged_data[1][merged_data[0].index(i[0])][2][1] = i[2]
            else:
                print(i)

        for i in data_lpg:
            if i[0] in merged_data[0]:
                merged_data[1][merged_data[0].index(i[0])][3][0] = i[1]
                merged_data[1][merged_data[0].index(i[0])][3][1] = i[2]
            else:
                print(i)

        return merged_data

    @staticmethod
    def insert_data(merged_data, average_data):
        downloader.create_database()

        # CONNECT TO DATABASE
        conn = sqlite3.connect("prices.db")
        c = conn.cursor()

        for i in range(0, len(merged_data[0])):
            line = '''
            INSERT INTO STATIONS (station_id, adress)
            VALUES (?, ?)
            '''

            c.execute(line, [i, merged_data[0][i]])

            line = '''
            INSERT INTO PRICE_E95 (station_id, price, date)
            VALUES (?, ?, ?)
            '''
            if merged_data[1][i][0][0] == 'Brak danych' or merged_data[1][i][0][0] == 'Niedostępne' or merged_data[1][i][0][0]==None:
                merged_data[1][i][0][0] = average_data[0][:-3].replace(',', '.')
            else:
                merged_data[1][i][0][0] = merged_data[1][i][0][0][:-3].replace(',', '.')
            c.execute(line, [i, merged_data[1][i][0][0], merged_data[1][i][0][1]])

            line = '''
            INSERT INTO PRICE_E98 (station_id, price, date)
            VALUES (?, ?, ?)
            '''

            if merged_data[1][i][1][0] == 'Brak danych' or merged_data[1][i][1][0] == 'Niedostępne' or merged_data[1][i][1][0]==None:
                merged_data[1][i][1][0] = average_data[1][:-3].replace(',', '.')
            else:
                merged_data[1][i][1][0] = merged_data[1][i][1][0][:-3].replace(',', '.')
            c.execute(line, [i, merged_data[1][i][1][0], merged_data[1][i][1][1]])

            line = '''
            INSERT INTO PRICE_ON (station_id, price, date)
            VALUES (?, ?, ?)
            '''

            if merged_data[1][i][2][0] == 'Brak danych' or merged_data[1][i][2][0] == 'Niedostępne' or merged_data[1][i][2][0]==None:
                merged_data[1][i][2][0] = average_data[2][:-3].replace(',', '.')
            else:
                merged_data[1][i][2][0] = merged_data[1][i][2][0][:-3].replace(',', '.')
            c.execute(line, [i, merged_data[1][i][2][0], merged_data[1][i][2][1]])

            line = '''
            INSERT INTO PRICE_LPG (station_id, price, date)
            VALUES (?, ?, ?)
            '''
            if merged_data[1][i][3][0] == 'Brak danych' or merged_data[1][i][3][0] == 'Niedostępne' or merged_data[1][i][3][0]==None:
                merged_data[1][i][3][0] = average_data[3][:-3].replace(',', '.')
            else:
                merged_data[1][i][3][0] = merged_data[1][i][3][0][:-3].replace(',', '.')
            c.execute(line, [i, merged_data[1][i][3][0], merged_data[1][i][3][1]])

        line = '''
        INSERT INTO AVG_PRICES (fuel, price)
        VALUES (?, ?)
        '''
        c.execute(line, ['E95', average_data[0][:-3].replace(',', '.')])
        c.execute(line, ['E98', average_data[1][:-3].replace(',', '.')])
        c.execute(line, ['ON', average_data[2][:-3].replace(',', '.')])
        c.execute(line, ['LPG', average_data[3][:-3].replace(',', '.')])

        conn.commit()
        conn.close()

    @staticmethod
    def read_data():
        # CONNECT TO DATABASE
        conn = sqlite3.connect("prices.db")
        c = conn.cursor()

        c.execute('''
                    SELECT
                        adress,
                        price,
                        date 
                    FROM 
                        PRICE_E95
                    INNER JOIN STATIONS ON STATIONS.station_id = PRICE_E95.station_id
                    ''')

        data_e95 = c.fetchall()

        c.execute('''
                    SELECT
                        adress,
                        price,
                        date 
                    FROM 
                        PRICE_E98
                    INNER JOIN STATIONS ON STATIONS.station_id = PRICE_E98.station_id
                    ''')

        data_e98 = c.fetchall()

        c.execute('''
                    SELECT
                        adress,
                        price,
                        date 
                    FROM 
                        PRICE_ON
                    INNER JOIN STATIONS ON STATIONS.station_id = PRICE_ON.station_id
                    ''')

        data_on = c.fetchall()

        c.execute('''
                    SELECT
                        adress,
                        price,
                        date 
                    FROM 
                        PRICE_LPG
                    INNER JOIN STATIONS ON STATIONS.station_id = PRICE_LPG.station_id
                    ''')

        data_lpg = c.fetchall()

        conn.close()

        result = downloader.merge_data(data_e95, data_e98, data_on, data_lpg)

        return result