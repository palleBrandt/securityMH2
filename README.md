### Resubmission
This is my resubmission, and this time it works. Logic follows as last time, but the program runs this time. 

All three clients share the same file/ source-code. But are configured with commanline arguments, see below.

To run the connections with TLC using the python SSL(outdated name) package, i have also created certificates for each participant (clients and server)

### Prerequisites
This project is build and tested with python3, but python should work fine also.

### How to run
First make sure you are standing in the resub directory, then open up four terminals, one for the hospital and three for the three clients.

#### Hospitial server
In the hospital terminal, run the following to start the hospital server. The hospital needs no arguments, as certificates and ports is coded in the sourcecode.
```
python hospital.py
```

#### Participents / Clients / Peers
For the three participents, we use the following format:
```
python3 peer.py <client_number> <own_port> <peer_port1> <peer_port2>"
```
Where clientnumber specified which certificate the individual client should use. own_port specified the clients own port. The peer_port1 and peer_port2 specifies the other two participants ports.

This means you will run the following three commands in the three terminals for the clients:
```
python3 client.py 1 5001 5002 5003
```

```
python3 client.py 2 5002 5001 5003
```

```
python3 client.py 3 5003 5001 5002
```

The hospital server should be started first.


