#!/usr/bin/env python3
import json, sys, requests, time

# Read from file
# if * ignore
# resp = http://freegeoip.net/json/$URL
# co-ords.lat = resp."latitude"
# co-ords.lon = resp."longitude"
# output html page with javascript points


def add_preamble(filename):
	pream = "<!DOCTYPE html>\n<html>\n\t<head>\n\t\t<style>\n\t\t\t#map {\n\t\t\t\theight: 400px;\n\t\t\t\twidth: 100%;\n\t\t\t}\n\t\t</style>\n\t</head>\n<body>\n\t<h3>GeoIP with Google Maps</h3>\n\t<div id=\"map\"></div>\n\t<script>\n\t\tfunction initMap() {\n\t\t\t"
	with open(filename, "w") as out:
		out.write(pream)

def add_js_preamble(filename):
	with open(filename, "w") as out:
		out.write("geoip_callback({\"type\":\"FeatureCollection\",\"features\":[")

def use_geoip_api(ip_addr):
	time.sleep(1) # Rate limiting
	url = "http://freegeoip.net/json/" + str(ip_addr)
	r = requests.get(url)
	if r.status_code != 200:
		print("Something is bad. Maybe the host is down?")
		return 0.0, 0.0
	else:
		print("Response: " + str(r.text) )
		data = json.loads(r.text)
		return data["latitude"], data["longitude"]

def into_js(input_file, filename):
	add_js_preamble(filename)
	count_id = 0
	output = ""
	with open(input_file, "r") as input_:
		with open(filename, "a") as out:
			for line in input_:
				if "*" in line:
					continue
				count_id += 1
				if line[0:14] == "traceroute to ":
					end_plus_one = line.index("(")
					if (end_plus_one != -1): # Found
						title = str(line[15:(end_plus_one - 1)])

				else:
					list_of_line = line.split(" ")
					if "192.168." in list_of_line[4]:
						continue
					elif "192.18." in list_of_line[4]:
						continue
					elif "10." in list_of_line[4]:
						continue
					else:
						#print(list_of_line)
						trimmed = list_of_line[4].replace("(", "").replace(")", "")
						lat, lng = use_geoip_api(trimmed)
						if (lat == "0.0"):
							if (lng == "0.0"):
								continue
						output += "{\"type\":\"Feature\",\"properties\":{\"url\":\"" + str(list_of_line[3]) + "\", \"ids\": \"," + str(count_id) + ",\"}, \"geometry\":{\"type\":\"Point\",\"coordinates\":[" + str(lat) + ", " + str(lng) + ", 0.0]},\"id\":\"" + str(count_id) + "\"},"

			out.write(output[:len(output) - 1] + "]});") # Remove last comma and add ending

into_js("traceroute_out.txt", "out.js")
