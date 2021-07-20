#!/usr/bin/env python
# coding: utf-8

####################################
# AUTHORS 
# -------
# 1. Siva Prakash Kuppuswamy 
# 2. Sundaravalli Aravazhi
####################################

import socket
import threading
from threading import *
import sys
import time as capture_time
import os
import struct
import argparse

parser = argparse.ArgumentParser(description='Go_Back_N_Client')
parser.add_argument('-i','--server_ip', type=str, help='Server ip address which you can find using ipconfig command on your server pc: Eg. -i 10.154.63.141', required=True)
parser.add_argument('-s','--server_port', type=int, help='Server port: Eg. -s 7735 (here it is 7735 in our connection)', required=True)
parser.add_argument('-f','--file_name', type=str, help='Name of the file to be uploaded: Eg. -f server_text.txt', required=True)
parser.add_argument('-m','--MSS', type=int, help='Maximum Segment Size(MSS): Eg. -m 500 ', required=True)
parser.add_argument('-n','--N', type=int, help='Window Size(N): Eg. -n 10 ', required=True)

args = vars(parser.parse_args()) 
print(args)

server_name = args["server_ip"]
server_port = args["server_port"]
MSS = args["MSS"]
N = args["N"]
file_name = args["file_name"]

# server_name = str(sys.argv[1])
# server_port = int(int(sys.argv[2]))
# MSS = int(sys.argv[3])
# N = int(sys.argv[4])
# file_name = sys.argv[5]

lock = threading.Lock()
ack_received = -1
total_packets = 0
transfer_data = []
sequence_number = 0
in_transit_packet_number = 0
retransmissions = 0
timestamp = []
data_packet = "0101010101010101"  
final_packet = "1111111111111111"  
ack_packet = "0b1010101010101010"  
retransmission_timeout = 500 
client_host = socket.gethostname()
client_ip = socket.gethostbyname(client_host)
client_port = 1234
bind_client_ip = "0.0.0.0" 

def create_packet(payload, packet_no, rcvd_packet_type):
    packet_type = int(rcvd_packet_type,2)
	# Packet data payload (decoding in string format from bytes)
    payload = payload.decode('utf-8')
    # Checksum computation
    check_sum_value = compute_checksum(payload)
    # Header formation
    header = struct.pack('!IHH', int(packet_no), int(check_sum_value), int(packet_type))
	# Packet data formation (encoding in byte format)
    payload = payload.encode('utf-8')
    # Packet with header and data returned
    packet_with_header = header + payload
    return packet_with_header

def deconstruct_packet(packet):
    header = struct.unpack('!IHH', packet) 
    ack_number = header[0]
    zeroes = header[1]
    packet_type = header[2]
    return ack_number, zeroes, packet_type

def compute_checksum(payload):
    check_sum = 0
    for i in range(0, len(payload), 2):
        if (i + 1) < len(payload):
            temp_sum = ord(payload[i]) + (ord(payload[i + 1]) << 8)
            temp_sum = temp_sum + check_sum
            check_sum = (temp_sum & 0xffff) + (temp_sum >> 16)
    check_sum_value = check_sum & 0xffff
    return check_sum_value

def handle_timeout():
    global in_transit_packet_number
    global timestamp
    global sequence_number
    if (in_transit_packet_number > 0) and ((int(round(capture_time.time() * 1000 )) - timestamp[sequence_number]) > retransmission_timeout):
            global retransmissions
            retransmissions = retransmissions + 1
            print("Time out, Sequence number: " + str(sequence_number))
            in_transit_packet_number = 0

def server_response_acks(client_socket):
    global in_transit_packet_number 
    global ack_received
    global sequence_number
    
    while sequence_number < total_packets:
        if (in_transit_packet_number > 0):
            data = client_socket.recv(2048)
            lock.acquire()
            ack_number, zero_value, packet_type = deconstruct_packet(data)          
            if (ack_number == sequence_number):
                in_transit_packet_number = in_transit_packet_number - 1
                ack_received = sequence_number
                sequence_number = sequence_number + 1
            else:
                in_transit_packet_number = 0
            lock.release()

def rdt_send(N, server_name, server_port):
    global client_socket
    global timestamp
    global sequence_number
    global in_transit_packet_number
    # global ack_received

    sequence_number = ack_received + 1 
    timestamp = [0.0]*total_packets
	
    while sequence_number < total_packets:
        lock.acquire()
        if (in_transit_packet_number < N):											
            packet_transfer = None
            if ((sequence_number + in_transit_packet_number) < total_packets):		
                packet_transfer = transfer_data[sequence_number + in_transit_packet_number]
                client_socket.sendto(packet_transfer,(server_name, server_port))
                timestamp[sequence_number + in_transit_packet_number] = int(round(capture_time.time() * 1000 ))
                in_transit_packet_number = in_transit_packet_number + 1

        handle_timeout()
        lock.release()

# def go_back_n_client_main():
if __name__ == '__main__':

    print("Client address: (", client_ip, ",", client_port, ")")
	
	#Server address
    print("Server address: (", server_name, ",", server_port, ")")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind((bind_client_ip, client_port))  
	
	#Run operation
    # 1. Reading the file
    if os.path.isfile(file_name):
        packet_number = 0
        f_in_1byte = ''
        read_file = open(file_name, 'rb')
        data_read = read_file.read(MSS)
        while data_read:
            transfer_data.append(create_packet(data_read, packet_number, data_packet))
            data_read = read_file.read(MSS)
            packet_number = packet_number + 1

        f_in_1byte = '0'
        f_in_1byte = f_in_1byte.encode('utf-8')
        transfer_data.append(create_packet(f_in_1byte, packet_number, final_packet))
        read_file.close()
        total_packets = len(transfer_data)
    else:
        print ('File Name does not match any files in the current folder \n')
        sys.exit()

    print("Total number of Packets generated from file : "+str(total_packets))

    start_time = int(round(capture_time.time() * 1000 ))

    # 2. Running the protocol to receive server response and upload the file
    ack_thread = threading.Thread(target= server_response_acks, args= (client_socket,))
    rdt_send_thread = threading.Thread(target= rdt_send, args = (N, server_name, server_port))
    ack_thread.start()
    rdt_send_thread.start()
    ack_thread.join()
    rdt_send_thread.join()

    end_time = int(round(capture_time.time() * 1000 ))

	#3. Printing output stats
    print("Total taken time for file transfer: ", (end_time - start_time)/1000, "s")
    print("Number of Retransmissions: ", str(retransmissions))

    if client_socket:
        client_socket.close()

# if __name__ == '__main__':
#     go_back_n_client_main()
