# Dequeue Enabled - Reliable User Data Gram Protocol with Encryption-Decryption 

> This particular repository contains the source code of the Reliable User Datagram Protocol for File transfer protocol

## The flow of the project goes like this
<br>

1. Actual transmission is on UDP & derudp is just an adaptor for the udp
2. Connection is established using three-way handshake mechanism between sender and receiver
3. There are two buffers in both sender and receiver
4. if connection established.. sends the packets to the two data buffer-queue.
5. Now if in data buffer-queue, 
	Derudp adopts 
	* queue-partition recognition
	* queue-partition reorganization

6. Both the sides, data in each buffer-queue has
	* buffer-queue name
	* data number flag (the packet start number and end number)
	* over-time variability
	* time-out flag
	* packets loss flag
	* packets retransmission data area
	* packets send data area
7. The retransmission data area stores the packet number to be retransmitted
8. The sending data area stores the packet number of the current queue to be sent.
9. The receiver also has the same buffer-queue used to store the received data packets
10. Extract the received data packet and reorder the unordered packets.



[todo]
* heartbeat packet to be checked
* Retranmission to be changed dynamically
* Need to fix the recurrsive error
* Need to plot the results and acculumate the content together
<br>
[Easily done]
	> can utilise the ftp, chat application
