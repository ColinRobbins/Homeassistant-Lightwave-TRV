import socket

TESTDATA = '*!{"trans":9647,"mac":"12:34:56","time":1582391210,"pkt":"868R","fn":"statusPush","prod":"valve","serial":"123456","type":"temp","batt":2.54,"ver":66,"state":"run","cTemp":20.6,"cTarg":20.0,"output":90,"nTarg":15.0,"nSlot":"21:00","prof":6}'

print ("Populating proxy...")
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
	msg = TESTDATA.encode("UTF-8")
	sock.sendto(msg, ("127.0.0.1", 9761))

print ("Reading from proxy...")
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
	sn = "123456"
	msg = sn.encode("UTF-8")
	sock.sendto(msg, ("127.0.0.1", 7878))
	response, dummy = sock.recvfrom(1024)
	msg = response.decode()
	if (msg == TESTDATA[2:]):
		print ("Read OK");
	else:
		print ("*** Read Error ***");

print ("Test error case...")
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sn = "9999"
        msg = sn.encode("UTF-8")
        sock.sendto(msg, ("127.0.0.1", 7878))
        response, dummy = sock.recvfrom(1024)
        msg = response.decode()
        if ("error" in msg): 
                print ("Error case OK");
        else:
                print ("*** Error error case ***");

