----------
PROJECT #2
----------
Name: Siva Prakash Kuppuswamy   Student ID: 200263687

Implementing Go Back N Automatic Repeat Request (ARQ) Scheme and Selective Repeat ARQ Protocol
_______________________________________________________________________________________________

Steps to run the file:
----------------------


------------------------------------------------------------------------------------------------------			
I> Server.py
------------------------------------------------------------------------------------------------------			
1.	a) From machine 1, go to the folder where server.py resides
	b) Execute using the following command in cmd:
	
			python3 Server.py -s <port> -f <filename> -p <probability>
		
		server_port: 7735
		filename: server_test.txt (any name would work)
		probability: 0.05 (will change for different test cases)

	c) For further help, run the following command in cmd:

			python3 Server.py -h

------------------------------------------------------------------------------------------------------			
II> Client.py
------------------------------------------------------------------------------------------------------		
2.	a) From machine 2, go to the folder where client.py resides and make sure the <test_file> resides                      in same folder. 
	b) Execute using the following command in cmd

			python3 Client.py -i <server_ip> -s <port> -m <MSS> -n <N> -f <filename>

		server_IP   : server's IP  
		server_port : 7735
		filename    : client_test_1mb_text_file.txt
		N           : 10  (will be change for different test cases)
		MSS         : 100 (will change for different test cases)

	c) For further help, run the following command in cmd:

			python3 Client.py -h

------------------------------------------------------------------------------------------------------			
Note : 1.Use python3 to run the files 
       2.First run the server and then client.
------------------------------------------------------------------------------------------------------			
	

	





 
