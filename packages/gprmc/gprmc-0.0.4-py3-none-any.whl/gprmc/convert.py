def convert_gprmc_data(_gprmc_data):
	GPRMC = _gprmc_data.split(",")
	GPRMC_details = {
    "Time":GPRMC[1],#UTC of position(hhmmss.ss)
    "Latitude":GPRMC[3],#Latitude (DDmm.mm)
    "Latitude_direction":GPRMC[4],#Latitude direction: (N = North, S = South)
    "Longitude":GPRMC[5],#Longitude (DDDmm.mm)
    "Longitude_direction":GPRMC[6],#Longitude direction: (E = East, W = West)
    "Date":GPRMC[9][:2]+'/'+GPRMC[9][2:4]+'/'+GPRMC[9][4:],#Date: dd/mm/yy

	}
	s_lat = float(GPRMC_details['Latitude'][:2])+float(GPRMC_details['Latitude'][2:])/60

	s_lon = float(GPRMC_details['Longitude'][:3])+float(GPRMC_details['Longitude'][3:])/60


	time = str(int(GPRMC_details['Time'][:2])+5)+str(int(GPRMC_details['Time'][2:4])+30)+GPRMC_details['Time'][4:6]


	return {"lat":s_lat,"lon":s_lon,"time":time,"date":GPRMC_details['Date']}