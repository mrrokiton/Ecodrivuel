class refactory_fuels:
    def __init__(self, consumption = 8, amount_to_refuel = 30, fuel_type = 'E95'):
        self.consumption = consumption
        self.amount_to_refuel = amount_to_refuel
        self.fuel_type = fuel_type

    def change_parameters(self, consumption = -1, amount_to_refuel = -1, fuel_type = ''):
        if consumption > 0:
            self.consumption = consumption
        if amount_to_refuel >= 0:
            self.amount_to_refuel = amount_to_refuel
        if fuel_type == 'E95' or fuel_type == 'E98' or fuel_type == 'ON' or fuel_type == 'LPG':
            self.fuel_type = fuel_type

    def add_costs_to_distances(self, distances):
        self.amount_to_refuel = self.amount_to_refuel.replace(',', '.')
        self.consumption = self.consumption.replace(',', '.')

        fuel_index = 0
        if self.fuel_type=='E98':
            fuel_index=1
        elif self.fuel_type=='ON':
            fuel_index=2
        elif self.fuel_type=='LPG':
            fuel_index=3

        for i in distances:
            if i['prices'][fuel_index][0]==None:
                continue
            cost_of_refueling = round(float(self.amount_to_refuel)*float(i['prices'][fuel_index][0]), 2)
            cost_of_fuel_to_drive = round(float(self.consumption)/100*float(i['distance'][:-3])*float(i['prices'][fuel_index][0]), 2)
            total_costs = round((cost_of_refueling + cost_of_fuel_to_drive), 2)
            i.update({'cost_of_refueling': str(cost_of_refueling)})
            i.update({'cost_of_fuel_to_drive': str(cost_of_fuel_to_drive)})
            i.update({'total_costs': str(total_costs)})
            print(i['address']+" "+i['distance']+" "+i['duration']+" "+i['cost_of_refueling']+' '+i['cost_of_fuel_to_drive']+' '+i['total_costs'])

        return [x for x in distances if x['prices'][fuel_index][0]!=None]
