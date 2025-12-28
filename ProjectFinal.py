import numpy as np
import matplotlib.pyplot as plt
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import pandas as pd
import time
dataset = pd.read_csv('FlightControl.csv')

#define ranges based on dataset
#everything 0-based indexing
altitude = ctrl.Antecedent(np.arange(0, 40001, 1000), 'altitude')
speed = ctrl.Antecedent(np.arange(0, 551, 1), 'speed')
pitch = ctrl.Antecedent(np.arange(-10, 16, 1),'pitch')
throttle = ctrl.Consequent(np.arange(0, 1.1, 0.01), 'throttle')

#automatic population with mf
altitude.automf(3, names=['low', 'medium', 'high'])
speed['slow'] = fuzz.trimf(speed.universe, [0, 0, 300])
speed['stable'] = fuzz.trimf(speed.universe, [250, 350, 450]) # 
speed['fast'] = fuzz.trimf(speed.universe, [400, 550, 550])

pitch['nose_down'] = fuzz.trimf(pitch.universe, [-10, -10, -2])
pitch['leveled'] = fuzz.trimf(pitch.universe, [-3, 0, 3]) 
pitch['nose_up'] = fuzz.trimf(pitch.universe, [2, 15, 15])

throttle['decrease'] = fuzz.trimf(throttle.universe, [0, 0, 0.5])#max decrease at -1
throttle['maintain'] = fuzz.trimf(throttle.universe, [0.15, 0.5, 0.85])
throttle['increase'] = fuzz.trimf(throttle.universe, [0.5, 1, 1])

#visualisation
#altitude.view()
#speed.view()
#pitch.view()
#throttle.view()

#rule creation
rule1 = ctrl.Rule(speed['fast'] | pitch['nose_down'], throttle['decrease'])
rule2 = ctrl.Rule(speed['stable'] & pitch['leveled'] , throttle['maintain'])
rule3 = ctrl.Rule(speed['slow'] | pitch['nose_up'], throttle['increase'])
rule4 = ctrl.Rule(speed['slow'] & pitch['nose_up'], throttle['increase'])#stalling danger
rule5 = ctrl.Rule(speed['slow'] & altitude['low'], throttle['increase'])#safety

#Control System Creation and Simulation
throttle_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5,])
flight = ctrl.ControlSystemSimulation(throttle_ctrl)

flight.input['altitude'] = 10000
flight.input['speed'] = 300
flight.input['pitch'] = 14

flight.compute()
result_percent=flight.output['throttle'] * 100
print("Simulating with numbers:\nAltitude: 10000 ft\nSpeed: 300 knots\nPitch: 14 deg")
print(f"Throttle should be adjusted to: {result_percent:.2f} percent ")
#print(flight.output['throttle']) #raw result from computation
throttle.view(sim=flight)
plt.show()


while(1):
    print("Do you wish to simulate with other numbers or numbers from the dataset?\nChoose from this menu:\n1: Use your own numbers\n2: Simulate and compare with selected line from the dataset\n3: Exit\n")
    ans=input("Enter answer here:")
    if ans == '3':
        print("Exiting...")
        break
    elif ans == '1':
        
        
        while(1):
            altitude_in = int(input("Enter altitude(<40000):"))
            if altitude_in<40000 and altitude_in>0:
                break
            else:
                print("Invalid input, try again")
        
        while(1):
            speed_in=int(input("Enter speed in knots(<551):"))
            if speed_in<551 and speed_in>0:
                break
            else:
                print("Invalid input, try again")

        while(1):
            pitch_in=int(input("Enter the pitch degree(between -10 and 15):"))
            if pitch_in<16 and pitch_in>-11:
                break
            else:
                print("Invalid input, try again")
    


        flight.input['altitude'] = altitude_in
        flight.input['speed'] = speed_in
        flight.input['pitch'] = pitch_in

        flight.compute()
        result_percent=flight.output['throttle'] * 100
        print("Simulating with your numbers....")
        print(f"Throttle should be adjusted to: {result_percent:.2f} percent ")
        #print(flight.output['throttle'])
        throttle.view(sim=flight)
        plt.show()
    elif ans == '2':
        row_choice = int(input(f"Enter the row number (1 to {len(dataset)}):"))
        if 1 <= row_choice <= len(dataset):
            selected_row = dataset.iloc[row_choice-1]#compensating for 0-based indexing
            
            flight.input['altitude'] = selected_row.iloc[0]
            flight.input['speed'] = selected_row.iloc[1]        #get the data from the row selected
            flight.input['pitch'] = selected_row.iloc[2]
            expected_adj = selected_row.iloc[3] #expected adjustment from dataset

            flight.compute()
            result_percent = flight.output['throttle'] * 100

            print("Results for this row are:")
            print(f"Inputs: Altitude: {selected_row.iloc[0]} ft, Speed: {selected_row.iloc[1]} knots, Pitch: {selected_row.iloc[2]} deg")
            print(f"Fuzzy output: {result_percent:.2f}% Throttle")
            print(f"Dataset says: {expected_adj}")
            time.sleep(3)

            throttle.view(sim=flight)
            plt.show()
        else:
            print("Invalid row number, returning to menu..")
            time.sleep(2)

    else:
        print("Invalid input, returning to menu..")
        time.sleep(2)