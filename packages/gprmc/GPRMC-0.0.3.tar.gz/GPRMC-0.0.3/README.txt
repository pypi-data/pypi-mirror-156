import gprmc2

print(gprmc2.convert('$GPRMC,125704.00,A,1304.91055,N,07737.23555,E,0.000,,250622,,,A*7A'))

{'lat': 13.0818425, 'lon': 77.6205925, 'time': '178704', 'date': '25/06/22'}