from DataDownloader import downloader
from api_management import api_management
from data_refactory import refactory_fuels

def download_data():
    Downloader = downloader()
    data_e95 = Downloader.download_fuel_values("https://cenapaliw.pl/stationer/e95/dolno-slaskie/wroclaw")
    data_e98 = Downloader.download_fuel_values("https://cenapaliw.pl/stationer/e98/dolno-slaskie/wroclaw")
    data_on = Downloader.download_fuel_values("https://cenapaliw.pl/stationer/on/dolno-slaskie/wroclaw")
    data_lpg = Downloader.download_fuel_values("https://cenapaliw.pl/stationer/lpg/dolno-slaskie/wroclaw")

    data_average = Downloader.download_average_fuel_values("https://autocentrum.pl/paliwa/ceny-paliw/dolnoslaskie")
    Downloader.close_tab()

    print("AVERAGE PRICES")
    for i in data_average:
        print(i)

    print("E95")
    for i in data_e95:
        print(i)
    print("E98")
    for i in data_e98:
        print(i)
    print("ON")
    for i in data_on:
        print(i)
    print("LPG")
    for i in data_lpg:
        print(i)

    places = []
    for i in data_e95:
        places.append(i[0])
        print(i[0])

    print("\n\nINNE MIEJSCA\n")

    for i in data_e98:
        if i[0] not in places:
            print(i[0])
    for i in data_on:
        if i[0] not in places:
            print(i[0])
    for i in data_lpg:
        if i[0] not in places:
            print(i[0])

    print("\n\nMERGED\n\n")

    merged = downloader.merge_data(data_e95, data_e98, data_on, data_lpg)
    for i in range(0, len(merged[0])):
        print(str(merged[0][i])+" "+str(merged[1][i]))

    downloader.insert_data(merged, data_average)

def read_data():
    data = downloader.read_data()

    return data

def calc_distances(data, fuel_type, refuel_amount, consumption, localization):
    Manager = api_management(TEST_VERSION=True)
    Factory = refactory_fuels()

    matrix = Manager.create_sets_for_api(localization, data)

    print("ORIGINS")
    for i in matrix[0]:
        print(i)
        print(len(i))
    print("DESTINATIONS")
    for i in matrix[1]:
        print(i)
        print(len(i))

    for i in range(0, len(matrix[0])):
        print(len(matrix[0][i])*len(matrix[1][i]))

    print("ALL AMOUNT")
    print(len(data[0]))

    Manager.get_distances(localization, data)
    Manager.save_result()
    result = Manager.refacture_result_distances()
    Factory.fuel_type=fuel_type
    Factory.amount_to_refuel=refuel_amount
    Factory.consumption=consumption
    result = Factory.add_costs_to_distances(result)

    for i in result:
        print(i)
    print(len(result))

    return result

def create_table(fuel_type, refuel_amount, consumption, localization):
    data = read_data()
    data = calc_distances(data, fuel_type, refuel_amount, consumption, localization)

    return data

if __name__== "__main__":
    # download_data()

    data = read_data()
    calc_distances(data)

    # downloader.create_database()

