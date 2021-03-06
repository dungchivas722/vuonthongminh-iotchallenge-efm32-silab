import pyrebase
import string
from datetime import datetime
import serial
import time
import array as arr

config = {
    "apiKey": "AIzaSyDBgPuvC6GeLorwmQRgnE51DK__9-i7Eik",
    "authDomain": "",
    "databaseURL": "https://iottest-d6c52-default-rtdb.firebaseio.com",
    "projectId": "iottest-d6c52",
    "storageBucket": "iottest-d6c52.appspot.com",
    "messagingSenderId": "200022699842",
    "appId": "1:200022699842:android:7bf5f158992f10bacc62db"
    

};
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
database = firebase.database()

class Vuon:
    def __init__(self, data_get):
        self.air = data_get["air"]                                          # độ ẩm không khí
        self.humidity_soil = data_get["humidity_soil"]                      # độ ẩm đất
        self.light = data_get["light"]                                      # Cường độ sáng 
        self.tempareture = data_get["tempareture"]                          # Nhiệt độ

        self.sw_light = data_get["sw_light"]                                # Bật đèn
        self.sw_pumb = data_get["sw_pumb"]                                  # Bật bơm   

        self.sw_st_light = data_get["sw_st_light"]                          # Bật thời gian đèn
        self.timeLightOn = data_get["timeLightOn"]                          # Thời gian đèn bật
        self.timeLightOff = data_get["timeLightOff"]                        # Thời gian đèn tắt

        self.sw_st_threshold = data_get["sw_st_threshold"]                  # Bật tưới cây theo ngưỡng
        self.threshold = data_get["threshold"]                              # Ngưỡng tưới
        self.threshold_max = data_get["threshold_max"]                      # Ngưỡng độ ẩm max

        self.sw_st_threshold_light = data_get["sw_st_threshold_light"]      # Đèn theo ngưỡng sáng
        self.threshold_light = data_get["threshold_light"]                  # Ngưỡng sáng min

        self.sw_st_water = data_get["sw_st_water"]                          # Tưới cây theo thời gian
        self.sw_st_water2 = data_get["sw_st_water2"]
        self.timeWater = data_get["timeWater"]                              # Thời gian tưới 
        self.timeWater2 = data_get["timeWater2"]                            # thời gian tưới

        self.time_water = data_get["time_water"]                            # Thời gian tưới kéo dài

def controlPump(humidity_soil, sw_pumb, sw_st_threshold, threshold, threshold_max, sw_st_water, sw_st_water2, timeWater, timeWater2, time_water):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S").split(":")
    time = int(current_time[0])*60+int(current_time[1])
    time1 = int(timeWater["hour"])*60+int(timeWater["minute"])
    time2 = int(timeWater2["hour"])*60+int(timeWater2["minute"])
    if sw_pumb == 1:
        return "t"
    if sw_st_threshold == 1:
        if humidity_soil >= int(threshold) and humidity_soil <= int(threshold_max):
            return "t"
    if sw_st_water == 1:
        if time >= time1 and time <= time1 + int(time_water):
            return "t"
        if time >= time2 and time <= time2 + int(time_water):
            return "t"
    return "f"

def controlLamp(light, sw_light, sw_st_light, timeLightOn, timeLightOff, sw_st_threshold_light, threshold_light):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S").split(":")
    time = int(current_time[0])*60+int(current_time[1])
    timeOn = int(timeLightOn["hour"])*60+int(timeLightOn["minute"])
    timeOff = int(timeLightOff["hour"])*60+int(timeLightOff["minute"])
    if sw_light == 1:
        return "c"
    if sw_st_light == 1:
        if time >= timeOn and time <= timeOff:
            return "c"
    if sw_st_threshold_light == 1:
        if light < threshold_light:
            return "c"
    return "k"
def up_data(database, path, data):
    database.child(path)
    database.set(data)



ser = serial.Serial ("/dev/ttyS0", 9600)    #ham mo cong port
def loc(data):
    if (data.isnumeric()==False): new = data.lstrip("+")
    else: return data
    return new

while(1):
    received_data = ser.read()              # lenh doc du
    time.sleep(0.05)
    data_left = ser.inWaiting()             #check for remaining byte
    received_data += ser.read(data_left)
    doc = received_data
    #print (doc)                        #print received data 
    docstring = doc.decode("utf-8")

    data_get = database.child("/data").get().val() # Lấy dữ liệu cloud
    vuon1 = Vuon(data_get[1])
    # vuon2 = Vuon(data_get[2])

    # Dữ liệu điều khiển
    p1 = controlPump(vuon1.humidity_soil, vuon1.sw_pumb, vuon1.sw_st_threshold, vuon1.threshold, vuon1.threshold_max, vuon1.sw_st_water, vuon1.sw_st_water2, vuon1.timeWater, vuon1.timeWater2, vuon1.time_water)
    l1 = controlLamp(vuon1.light, vuon1.sw_light, vuon1.sw_st_light, vuon1.timeLightOn, vuon1.timeLightOff, vuon1.sw_st_threshold_light, vuon1.threshold_light)
    # p2 = controlPump(vuon2.humidity_soil, vuon2.sw_pumb, vuon2.sw_st_threshold, vuon2.threshold, vuon2.threshold_max, vuon2.sw_st_water, vuon2.sw_st_water2, vuon2.timeWater, vuon2.timeWater2, vuon2.time_water)
    # l2 = controlLamp(vuon2.light, vuon2.sw_light, vuon2.sw_st_light, vuon2.timeLightOn, vuon2.timeLightOff, vuon2.sw_st_threshold_light, vuon2.threshold_light)
    viet = p1+l1
    ser.write(viet.encode()) 

    humidity_soil1 = int(loc(docstring[28:32]))   # Cập nhập thông số đo được vào đây
    tempareture1 = int(loc(docstring[16:20]))
    light1 = int(loc(docstring[4:8]))
    air1 = int(loc(docstring[10:14]))
    # humidity_soil2 = 0
    # tempareture2 = 0
    # light2 = 0
    # air2 = 0
    
    up_data(database, "data/1/air", air1)
    up_data(database, "data/1/humidity_soil", humidity_soil1)
    up_data(database, "data/1/light", light1)
    up_data(database, "data/1/tempareture", tempareture1)
    # up_data(database, "data/2/air", air2)
    # up_data(database, "data/2/humidity_soil", humidity_soil2)
    # up_data(database, "data/2/light", light2)
    # up_data(database, "data/2/tempareture", tempareture2)







# ser = serial.Serial ("/dev/ttyS0", 9600)    #ham mo cong port
# def loc(data):
#     if (data.isnumeric()==False): new = data.lstrip("+")
#     else: return data
#     return new

# while(1):
#     data_get = database.child("/data").get().val() # Lấy dữ liệu cloud
#     vuon1 = Vuon(data_get[1])
#     vuon2 = Vuon(data_get[2])

#     # Dữ liệu điều khiển
#     p1 = controlPump(vuon1.humidity_soil, vuon1.sw_pumb, vuon1.sw_st_threshold, vuon1.threshold, vuon1.threshold_max, vuon1.sw_st_water, vuon1.sw_st_water2, vuon1.timeWater, vuon1.timeWater2, vuon1.time_water)
#     l1 = controlLamp(vuon1.light, vuon1.sw_light, vuon1.sw_st_light, vuon1.timeLightOn, vuon1.timeLightOff, vuon1.sw_st_threshold_light, vuon1.threshold_light)
#     p2 = controlPump(vuon2.humidity_soil, vuon2.sw_pumb, vuon2.sw_st_threshold, vuon2.threshold, vuon2.threshold_max, vuon2.sw_st_water, vuon2.sw_st_water2, vuon2.timeWater, vuon2.timeWater2, vuon2.time_water)
#     l2 = controlLamp(vuon2.light, vuon2.sw_light, vuon2.sw_st_light, vuon2.timeLightOn, vuon2.timeLightOff, vuon2.sw_st_threshold_light, vuon2.threshold_light)
    
#     humidity_soil1 = 0  # Cập nhập thông số đo được vào đây
#     tempareture1 = 0
#     light1 = 0
#     air1 = 0
#     humidity_soil2 = 0
#     tempareture2 = 0
#     light2 = 0
#     air2 = 0
    
#     up_data(database, "data/1/air", air1)
#     up_data(database, "data/1/humidity_soil", humidity_soil1)
#     up_data(database, "data/1/light", light1)
#     up_data(database, "data/1/tempareture", tempareture1)
#     up_data(database, "data/2/air", air2)
#     up_data(database, "data/2/humidity_soil", humidity_soil2)
#     up_data(database, "data/2/light", light2)
#     up_data(database, "data/2/tempareture", tempareture2)

# while True:
#     #while viet!='0' :
#     received_data = ser.read()              # lenh doc du
#     time.sleep(0.05)
#     data_left = ser.inWaiting()             #check for remaining byte
#     received_data += ser.read(data_left)
#     doc = received_data
#     #print (doc)                        #print received data 
#     docstring = doc.decode("utf-8")
#     #print(docstring);
#     data1s=int(loc(docstring[4:8]))
#     data2s=int(loc(docstring[10:14]))
#     data3s=int(loc(docstring[16:20]))
#     data4s=int(loc(docstring[22:26])) 
#     data5s=int(loc(docstring[28:32])) 
#     print(data1s,data2s,data3s,data4s,data5s)
