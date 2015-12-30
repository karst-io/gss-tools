#!/usr/bin/env python

import sys
import os
import json
import uuid
import logging

def throw_warning(logline, warning):
	logging.warning(logline)
	logging.warning(warning)

def dms_to_dd(dms):
	try:
		hour = float(dms[0:2])
		minutes = float(dms[2:4])
		seconds = float(dms[4:6])
		return (hour + (minutes/60) + (seconds/3600))
	except ValueError:
		return False

FORMAT = '%(levelname)s: %(message)s'
logging.basicConfig(format=FORMAT)

accuracy_dict = {
	" ": -1,
	"": -1,
	"?": -1,
	"Z": -1,
	"F": -1,
	"G": -1,
	"H": 55,
    "I": 100,
    "J": 200,
    "K": 300,
    "L": 550,
    "M": 1000,
    "N": 2000,
    "O": 3000,
    "P": 5280,
    "Q": 2*5280,
    "R": 3*5280,
    "S": 5*5280,
}

output_dir = "output/"

fptr = open('gsslist.txt','r')

for line in fptr.readlines():
	if line [0:3] == "  G":
		line = line.strip()
		code = line[0:7].replace(" ","")
		name = line[11:35].strip()
		record_type = line[7:9].strip()
		lat = dms_to_dd(line[37:44])
		lon = dms_to_dd(line[44:51]) * -1 
		accuracy = line[51:52]

		topo_indicator = line[60:61]
		elevation = line[61:66].strip()
		entry_status = line[66:68].strip()
		equipment = line[67:69].strip()
		entrance_type = line[69:70].strip()
		field_indication = line[70:71].strip()

		length = line[77:84].strip()
		depth = line[84:89].strip()

		if record_type == 'E':
			if accuracy not in ["H","I","J","K","L","M","N","O","P","Q","R","S"]:
				throw_warning(line, "Accuracy for %s is '%s'" % (code, accuracy))

			#print "%s: %s" % (code,name)
			#print 'accuracy: %s' % accuracy

			cave_file_path = "%s/%s.json" % (output_dir, code)

			#create new one
			entrance_obj = 	{
								'id': str(uuid.uuid4()),
								'name': name,
								'coordinates': [
									{
										'id': str(uuid.uuid4()),
										'system': 'NAD27',
										'lat': lat,
										'lon': lon,
										'accuracy': accuracy_dict[accuracy],
										'submitter': 'GSS',
										'submitted': '1990-01-01'
									}
								],
								'elevation': elevation,
								'status': 'UNKNOWN',
								'ownership': 'UNKNOWN',
								'type': 'UNKNOWN',
								'negotiation': 'UNKNOWN',
								'formation': 'NATURAL',
								'location': 'UNKNOWN',
								'characteristics': 'UNKNOWN',
								'hydrology': 'UNKNOWN',
								'hazards': 'UNKNOWN',
							}

			if entry_status == 'B':
				#BIOLOGICALLY SIGNIFICANT; ASK PERMISSION
				entrance_obj['status'] = 'PERMISSION REQUIRED',
				entrance_obj['status_description'] = 'Biologically significant; ask permission'
			elif entry_status == 'C':
				#commercial cave
				entrance_obj['ownership'] = 'COMMERCIAL'
			elif entry_status == 'D':
				#govt
				entrance_obj['status'] = 'DESTROYED'
			elif entry_status == 'G' or entry_status == 'K':
				#govt park
				entrance_obj['ownership'] = 'GOVERNMENT'
			elif entry_status == 'L':
				#locked/gated
				entrance_obj['status'] = 'LOCKED / GATED'
			elif entry_status == 'N':
				#forbidden
				entrance_obj['status'] = 'FORBIDDEN'
			elif entry_status == 'P':
				#private
				entrance_obj['ownership'] = 'PRIVATE PROPERTY'
			elif entry_status == 'S':
				#NSS
				entrance_obj['ownership'] = 'CONSERVANCY'
			else:
				throw_warning(line, "Unknown entry status %s" % entry_status)

			if entrance_type == 'E' or entrance_type == 'L':
				entrance_obj['type'] = 'HORIZONTAL'
				entrance_obj['type_description'] = 'extremely big, over 20 feet wide and/or high'
				entrance_obj['formation'] = 'NATURAL'
				entrance_obj['negotiation'] = 'WALK'
			elif entrance_type == 'F':
				entrance_obj['type'] = 'HORIZONTAL'
				entrance_obj['negotation'] = 'SWIM'
				entrance_obj['hydrology'] = 'SUBMERGED'
			elif entrance_type == 'H':
				entrance_obj['type'] = 'HORIZONTAL'
				entrance_obj['type_description'] = 'stoop or duck walk'
				entrance_obj['negotiation'] = 'STOOP'
			elif entrance_type == 'K':
				entrance_obj['type'] = 'HORIZONTAL'
				entrance_obj['negotiation'] = 'CRAWL'
			elif entrance_type == 'T':
				entrance_obj['type'] = 'HORIZONTAL'
				entrance_obj['formation'] = 'ARTIFICIAL'
			elif entrance_type == 'A':
				entrance_obj['type'] = 'VERTICAL'
				entrance_obj['formation'] = 'ARTIFICIAL'
			elif entrance_type == 'B':
				entrance_obj['type'] = 'VERTICAL'
				entrance_obj['negotiation_description'] = 'bottleneck (small but bells out)'
			elif entrance_type == 'C':
				entrance_obj['type'] = 'VERTICAL'
				entrance_obj['negotiation'] = 'CLIMB'
				entrance_obj['negotiation_description'] = 'chimney or climb-down'
			elif entrance_type == 'O':
				entrance_obj['type'] = 'VERTICAL'
				entrance_obj['negotiation'] = 'RAPPEL'
			elif entrance_type == 'P':
				entrance_obj['type'] = 'VERTICAL'
				entrance_obj['negotiation'] = 'RAPPEL'
			else:
				throw_warning(line, "unknown entrance type '%s'" % entrance_type)


			if field_indication == 'B':
				entrance_obj['field_indication'] = 'BLUFF OR HEADWALL'
			elif field_indication == 'H':
				entrance_obj['field_indication'] = 'HILLSIDE'
			elif field_indication == 'I':
				entrance_obj['hydrology'] = 'WATER IN'
			elif field_indication == 'L':
				entrance_obj['field_indication'] = 'BENCH'
			elif field_indication == 'P':
				entrance_obj['hydrology'] = 'LAKE OR POOL'
				entrance_obj['field_indication'] = 'SINK'
			elif field_indication == 'Q':
				entrance_obj['field_indication'] = 'QUARRY'
			elif field_indication == 'R':
				entrance_obj['field_indication'] = 'ROAD CUT'
			elif field_indication == 'S':
				entrance_obj['field_indication'] = 'SINK'
				entrance_obj['hydrology'] = 'NONE'
			elif field_indication == 'W':
				entrance_obj['field_indication'] = 'STREAMBED'
			elif field_indication == 'X':
				entrance_obj['hydrology'] = 'WATER OUT'

			if os.path.exists(cave_file_path) == True:
				#one already exists; load it
				fptr = open(cave_file_path,'r')
				cave_obj = json.loads(fptr.read())

				cave_obj['entrances'].append(entrance_obj)

			else:
				
				#cave does not exist; create a new cave object
				cave_obj = 	{
							'id': str(uuid.uuid4()), 
							'code': code, 
							'name': name, 
							'entrances': [ entrance_obj ],
							'length': length,
							'depth': depth
							}

			#save output
			fptr = open(cave_file_path,'w')
			fptr.write(json.dumps(cave_obj))
			fptr.close()
		else:
			print "WARN: %s" % record_type

