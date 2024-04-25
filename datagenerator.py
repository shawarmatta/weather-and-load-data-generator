import csv
import random
import math
import sys

stages = 3
days = 18
hours = 24
nbOfDataPoints = stages*days*hours
# Parameters for electricity prices
initial_price_electricity = 0.93  # Initial price in euros per kWh
drift_electricity = 0.05  # Drift per half hour
volatility_electricity = 0.0252  # Volatility per half hour
time_intervals_electricity = 1  # Time interval in hours
factorHydrogen=500;
factorElectricity=200;

file_path=None
#file_path = r'C:\Users\rmatta\Desktop\Thesis\Data generation\datagenerator\generated_data.csv'
if not file_path:
    print('Specify path')
    sys.exit()

'''
Winter:
day 1: sunny, lightly windy
day 2:lightly sunny, lightly windy
day 3: lightly sunny, windy
day 4: not sunny,  windy
day 5: not sunny, very windy (weight=2)

Fall:
day 6:  sunny, not windy
day 7: lightly sunny, lightly windy (weight=2)
day 8: not sunny, windy
day 9: not sunny, very windy

Spring:
day 10: very sunny, not windy
day 11: sunny, lightly windy
day 12: lightly sunny, lightly windy (weight=2)
day 13: not sunny, windy

Summer
day 14: very sunny, not windy (weight=2)
day 15: sunny, lightly windy
day 16: lightly sunny, lightly windy
day 17: not sunny,  windy
day 18: not sunny, windy
'''

# Function to generate values for yh based on specified patterns
def generate_values_yh(day, hour):
    if ((day >= 1 and day <= 9) and hour >= 8 and hour <= 20):
        if hour <= 12:
            return abs((2 + (4/day) * 2 + hour - 8 + random.normalvariate(0, 2))*factorHydrogen)
        else:
            return abs((11 + (4/day) * 2 + 12 - (hour - 12) + random.normalvariate(0, 2))*factorHydrogen)
    elif ((day >= 10 and day <= 18) and hour >= 8 and hour <= 20):
        if hour <= 12:
            return abs((1 + (4/day) * 2 + hour - 8 + random.normalvariate(0, 2))*factorHydrogen)
        else:
            return abs((9 + (4/day) * 2 + 12 - (hour - 12) + random.normalvariate(0, 2))*factorHydrogen)
    else:
        return abs(((4/day) * 2 + random.normalvariate(0, 2))*factorHydrogen)  # A general lower value for yh

# Function to generate values for ye based on specified patterns
def generate_values_ye(day, hour):
    if ((day >= 1 and day <= 9) and hour >= 8 and hour <= 20):
        if hour <= 12:
            return abs((13 + (4/day) * 2 + hour - 8 + random.normalvariate(0, 2))*factorElectricity)
        else:
            return abs((13 + (4/day) * 2 + 12 - (hour - 12) + random.normalvariate(0, 2))*factorElectricity)
    elif ((day >= 10 and day <= 18) and hour >= 8 and hour <= 20):
        if hour <= 12:
            return abs((13 + (4/day) * 2 + hour - 8 + random.normalvariate(0, 2))*factorElectricity)
        else:
            return abs((13 + (4/day) * 2 + 12 - (hour - 12) + random.normalvariate(0, 2))*factorElectricity)
    else:
        return abs((14+2 + (4/day) * 2 + random.normalvariate(0, 2))*factorElectricity)  # A general lower value for ye


def generate_electricity_prices(initial_price, drift, volatility, time_intervals, num_points):
    electricity_prices = []
    for i in range(num_points):
        Wt = math.sqrt(time_intervals) * random.gauss(0, 1)
        St = initial_price * math.exp((drift - 0.5 * volatility**2) * time_intervals + volatility * Wt)
        electricity_prices.append(St)
    return electricity_prices


def generate_values_ypv(day, hour):  # Kwh/m^2/hour
    if ((1 <= day <= 5 and hour <= 8) or
        (1 <= day <= 5 and 17 <= hour <= 23) or
        (6 <= day <= 9 and hour <= 7) or
        (6 <= day <= 9 and 18 <= hour <= 23) or
        (10 <= day <= 13 and hour <= 7) or
        (10 <= day <= 13 and 19 <= hour <= 23) or
        (14 <= day <= 18 and hour <= 6) or
        (14 <= day <= 18 and 21 <= hour <= 23)):
        return 0
    
    if day == 1 or day == 6 or day == 11 or day == 15:
        # Sunny
        if hour <= 12:
            return random.uniform(0.5, 0.8) * (hour / 12.0)  # Increasing before 12 PM
        else:
            return random.uniform(0.5, 0.8) * (1.0 - (hour - 12) / 12.0) # Decreasing after 12 PM
    elif day == 2 or day == 3 or day == 7 or day == 12 or day == 16:
        # Lightly sunny
        if hour <= 12:
            return random.uniform(0.2, 0.5) * (hour / 12.0) # Increasing before 12 PM
        else:
            return random.uniform(0.2, 0.5) * (1.0 - (hour - 12) / 12.0)  # Decreasing after 12 PM
    elif day == 4 or day == 5 or day == 8 or day == 9 or day == 13 or day == 17 or day == 18:
        # Not sunny
        if hour <= 12:
            return random.uniform(0.0, 0.2) * (hour / 12.0) # Increasing before 12 PM
        else:
            return random.uniform(0.0, 0.2) * (1.0 - (hour - 12) / 12.0)  # Decreasing after 12 PM
    elif day == 10 or day == 14:
        # Very sunny
        if hour <= 12:
            return random.uniform(0.8, 1.0) * (hour / 12.0) # Increasing before 12 PM
        else:
            return random.uniform(0.8, 1.0) * (1.0 - (hour - 12) / 12.0)  # Decreasing after 12 PM
    else:
        return 0.0  # A default value


def generate_values_ywt(day):
    if day == 1 or day == 2 or day == 7 or day==11 or day == 12 or day == 15 or day == 16:
        return random.uniform(0.2, 0.5)*14  # lightly windy
    elif day == 3 or day == 4 or day == 8 or day == 13 or day == 17 or day == 18:
        return random.uniform(0.6, 0.8)*14  # windy
    elif day == 5 or day == 9:
        return random.uniform(0.8, 1.0)*14  # very windy
    elif day == 6 or day == 10 or day == 14:
        value = random.uniform(0.0, 0.2) * 20   # not windy
        if value < 3.5:
            return 0
        else:
            return value
    else:
        return 0.0  # A default value

'''
Winter:
day 1: sunny, lightly windy
day 2:lightly sunny, lightly windy
day 3: lightly sunny, windy
day 4: not sunny,  windy
day 5: not sunny, very windy (weight=2)

Fall:
day 6:  sunny, not windy
day 7: lightly sunny, lightly windy (weight=2)
day 8: not sunny, windy
day 9: not sunny, very windy

Spring:
day 10: very sunny, not windy
day 11: sunny, lightly windy
day 12: lightly sunny, lightly windy (weight=2)
day 13: not sunny, windy

Summer
day 14: very sunny, not windy (weight=2)
day 15: sunny, lightly windy
day 16: lightly sunny, lightly windy
day 17: not sunny,  windy
day 18: not sunny, windy
'''

# Generate electricity prices
electricity_prices = generate_electricity_prices(initial_price_electricity, drift_electricity, volatility_electricity, time_intervals_electricity, nbOfDataPoints)



# Write data to CSV file
with open(file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Stage', 'Day', 'Hour', 'PV', 'WT', 'Electricity Load', 'Hydrogen Load', 'Electricity Prices'])

    for s in range(stages):
        for d in range(1, days + 1):
            for t in range(hours):
                ypv = generate_values_ypv(d, t)
                ye = generate_values_ye(d, t)
                yh = generate_values_yh(d, t)
                ywt = generate_values_ywt(d)
                index = s * days * hours + (d - 1) * hours + t
                if index < nbOfDataPoints:  # Check if index is within the range
                    writer.writerow([s, d, t+1, ypv, ywt, ye, yh, electricity_prices[index]])
                else:
                    print(f"Index {index} out of range for electricity prices.")

print("Data has been generated and exported to generated_data.csv.")





