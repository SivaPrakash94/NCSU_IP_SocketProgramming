#!/usr/bin/env python
# coding: utf-8

####################################
# AUTHORS 
# -------
# 1. Siva Prakash Kuppuswamy 
# 2. Sundaravalli Aravazhi
####################################

import time as capture_time
import socket
import sys
import random
import struct
import math
import argparse

parser = argparse.ArgumentParser(description='Go_Back_N_Server')
parser.add_argument('-s','--server_port', type=int, help='Server port: Eg. -s 7735 (here it is 7735 in our connection)', required=True)
parser.add_argument('-f','--file_name', type=str, help='Name of the file to be downloaded: Eg. -f server_text.txt', required=True)
parser.add_argument('-p','--loss_probability', type=float, help='Packet loss probability: Eg. -p 0.05 ', required=True)

args = vars(parser.parse_args()) 
print(args)


server_port = args["server_port"]
file_name = args["file_name"]
packet_loss_prob = args["loss_probability"]  
client_port = 1234

# server_port = int(sys.argv[1])
# file_name = sys.argv[2]
# packet_loss_prob = float(sys.argv[3]) 

host_name = '0.0.0.0'
previous_value = -1
FP = open(file_name,"w") 
packet_data_16bits = "0101010101010101"
packet_ack_16bits = "1010101010101010"
zeros_16bits = "0000000000000000"
fin_16bits = '1111111111111111'

def ack_packet(server_socket, client_address, sequence_number,zeros_16bits,packet_type):
	tcp_header = struct.pack("!IHH",sequence_number,int(zeros_16bits, 2),int(packet_type, 2))
	server_socket.sendto(tcp_header,client_address)

def deconstruct_packet(packet):
	tcp_header = struct.unpack('!IHH', packet[0:8]) 
	sequence_number = tcp_header[0]
	check_sum = tcp_header[1]
	packet_type = tcp_header[2]
	data = packet[8:] 
	data = data.decode('utf-8')
	return sequence_number, check_sum, packet_type , data

def checksum_computation(packet):
	sum = 0
	check_sum = 0
	for i in range(0, len(packet), 2):
		if (i + 1) < len(packet):
			temp_sum = ord(packet[i]) + (ord(packet[i + 1]) << 8)
			temp_sum = temp_sum + sum
			sum = (temp_sum & 0xffff) + (temp_sum >> 16)
	check_sum = (~sum & 0xffff)
	return check_sum
	
def go_back_n_server_main():
  
	global client_port
	global host_name
	global server_port
	global file_name
	global packet_loss_prob     
	global previous_value   
	global FP 
	global server_socket
	global packet_data_16bits
	global packet_ack_16bits 
	global fin_16bits
	global zeros_16bits

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_ip = socket.gethostbyname(socket.gethostname())
	server_socket.bind((host_name,server_port))
	print("Server started and is listening at port number: ",server_port)

	start_time = int(round(capture_time.time() * 1000 ))
	end_time = 0
	last_byte_of_file_received = False	

	while last_byte_of_file_received != True:
		data, addr = server_socket.recvfrom(2048)
		client_host_name = addr[0]
		sequence_number, received_checksum, packet_type, data = deconstruct_packet(data)
		if (checksum_computation(data) & received_checksum != 0) :
			print('Faulty Checksum, sequence number = ', str(sequence_number))

		else:
			if sequence_number == previous_value + 1 and random.uniform(0, 1) > packet_loss_prob:
				if packet_type == int(fin_16bits, 2):                                      
					ack_packet(server_socket, (client_host_name, client_port), sequence_number, zeros_16bits, packet_ack_16bits)
					end_time = int(round(capture_time.time() * 1000 ))
					print("Data download is complete")
					last_byte_of_file_received = True
					break
				
				ack_packet(server_socket, (client_host_name,client_port), sequence_number, zeros_16bits, packet_ack_16bits)
				previous_value += 1
				FP.write(data)							
			else:
				print('Packet loss, sequence number = ', str(sequence_number))

	print("Total time taken for file reception :", (end_time - start_time)/1000)
	FP.close()
	server_socket.close()

if __name__ == '__main__':
	go_back_n_server_main()