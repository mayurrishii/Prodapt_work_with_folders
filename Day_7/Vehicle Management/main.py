from car import Car
from ev import EV
from polymorphism import Overloadingdemo
from polymorphism import overloading
from report_export import export_vehicle_data
from exception import VehicleError, OwnerAlreadyExistsError, InvalidBatteryCapacityError



def main():
    try:
        car1 = Car("Toyota", "Camry", 2020)
        car2 = EV("Honda", "Civic", 2022,75)

        car1.set_owner("Alice")
        car2.set_owner("Bob")

        vehicles = [car1,car2]

        print(car1.show_info(), car1.get_owner())  # Output: Alice
        print(car2.show_info(), car2.get_owner())  # Output: Bob

        print("\nOverloading demo")
        overloading()

        print("\nExporting vehicle data to CSV")
        export_vehicle_data("vehicle_data.csv", vehicles)
    except VehicleError as e:
        print(f"An error occurred: {e}")
    

main()
"""
overloading()


a = Car("Toyota", "Camry", 2020, "Mayur")  # Passing owner name as an argument

b = Car("Honda", "Civic", 2022, "Jane Smith")  # Passing owner name as an argument

ev1 = EV("Tesla", "Model3", 2021, 100)

# a.set_owner("Rishi")

export_vehicle_data("vehicle_data.csv", [a, b, ev1])

# ev1.show_info()
# a.start_engine()
# ev1.charge_battery()


# print(a.brand)  # Output: Toyota
# print(a.get_owner())  # Output: Mayur
# a.set_owner("Alice Johnson")  # Changing the owner using the setter method
# print(a.get_owner())  # Output: Alice Johnson

# l = [a, b]

# for car in l:
#     car.start_engine()
#     car.show_info()

"""