import requests
import smtplib
import googlemaps
import pandas as pd
import pickle
import time
from tqdm import tqdm

class api_management:

    def __init__(self, TEST_VERSION = False):
        api_file = open('api-key.txt', 'r')
        self.__api_key = api_file.read()
        api_file.close()

        self.__base_url = "https://maps.googleapis.com/maps/api/distancematrix/json?"
        self.__TEST_VERSION = TEST_VERSION

        self.__adress_from = ""
        self.__last_search = None

        self.__gmaps = googlemaps.Client(key=self.__api_key)

        self.__result_distances = None

    def create_sets_for_api(self, adres_from, merged_data):

        set_size = 15

        sets_of_origin = []
        sets_of_destination = []
        num_of_whole_sets = int(len(merged_data[0])/set_size)

        for i in range(0, num_of_whole_sets):
            set_destination = []

            for j in range(i*set_size, (i+1)*set_size):
                set_destination.append([merged_data[0][j], merged_data[1][j]])

            sets_of_origin.append([adres_from])
            sets_of_destination.append(set_destination)

        if num_of_whole_sets*set_size != len(merged_data[0]):
            set_destination = []
            for i in range(num_of_whole_sets*set_size, len(merged_data[0])):
                set_destination.append([merged_data[0][i], merged_data[1][i]])
            sets_of_origin.append([adres_from])
            sets_of_destination.append(set_destination)

        return  [sets_of_origin, sets_of_destination]

    def get_distances(self, adress_from, merged_data):
        if adress_from == self.__adress_from:
            return self.__result_distances

        matrix = self.create_sets_for_api(adress_from, merged_data)

        if self.__TEST_VERSION:
            print("ORIGINS")
            for i in matrix[0]:
                print(i)
                print(len(i))
            print("DESTINATIONS")
            for i in matrix[1]:
                for j in i:
                    print(j[0])
                print(len(i))

            print("ALL AMOUNT")
            print(len(merged_data[0]))


        result_table = []
        for i in tqdm(range(0, len(matrix[0]))):
            result_table.append([self.__gmaps.distance_matrix(matrix[0][i], [ x[0] for x in matrix[1][i] ]), [ x[1] for x in matrix[1][i] ]])
            time.sleep(1)

        self.__adress_from = adress_from
        self.__result_distances = result_table

        return result_table

    def save_result(self):
        with open('result.dictionary', 'wb') as file_result:
            pickle.dump(self.__result_distances, file_result)

    def load_result(self):
        result = []
        with open('result.dictionary', 'rb') as file_result:
            result = pickle.load(file_result)
        return result

    def refacture_result_distances(self):
        result = self.load_result()

        for i in result:
            print(i)

        addresses = []

        for set in result:
            for i in range(0, len(set[0]['destination_addresses'])):
                if set[0]['rows'][0]['elements'][i]['status'] == 'OK':
                    addresses.append({'address': set[0]['destination_addresses'][i],
                                      'distance': set[0]['rows'][0]['elements'][i]['distance']['text'],
                                      'duration': set[0]['rows'][0]['elements'][i]['duration']['text'],
                                      'prices': set[1][i]})

        return addresses