#!/usr/bin/env python3

from concurrent import futures
import sys  # For sys.argv, sys.exit()
import socket  # for gethostbyname()

import grpc

import csci4220_hw3_pb2
import csci4220_hw3_pb2_grpc

import math

#global variable k_buckets[]
# localnode=csci4220_hw3_pb2.Node()
# k=0
k_buckets=[]
key_values={}


#define XOR operator
def XOR(targetid,localid):
	return targetid^localid

# def get_bucket_layer(targetid,localid):
# 	distance=targetid^localid
# 	return floor(log(distance,2))



#print k_buckets
def print_buckets():
	global k_buckets
	#print("hello i am here")
	for i in range(0,4):
		print("%d:"%i,end='')
		# print("for debug1: %d"%len(k_buckets[i]))
		if len(k_buckets[i])==0 :
			print()
		else:
			for node in k_buckets[i]:
				print(" ",end='')
				print("%d:%d"%(node.id,node.port),end='')
			print()

def sort_buckets(k_buckets):
	sorted_nodes=[]
	for node_list in k_buckets:
		for node in node_list:
			sorted_nodes.append(node)
	sorted_nodes.sort(key=lambda x: XOR(target_id, x.id))
	return sorted_nodes


#find the closest k nodes
def find_k_closest(k_buckets,localnode,target_id,requester_id,k):
	sorted_nodes=[]
	for node_list in k_buckets:
		if len(node_list)>0:
			for node in node_list:
				sorted_nodes.append(node)
	#_buckets( )
	#print("length is %d"%len(sorted_nodes))
	sorted_nodes.sort(key=lambda x:XOR(target_id,x.id))
	#print("after sort length is %d"%len(sorted_nodes))
	closest_nodes = csci4220_hw3_pb2.NodeList(responding_node=localnode)
	if len(sorted_nodes)> 0:
		count = 0
		for i in range(0,len(sorted_nodes)):
			if sorted_nodes[i].id != requester_id:
				closest_nodes.nodes.append(sorted_nodes[i])
				count+=1
			if count == k :
				break
	# distance=self_id^target_id
	# dis=1
	# count=0
	# closest_nodes=csci4220_hw3_pb2.NodeList()
	# for i in range(math.floor(log(distance,2)),-1,-1):
	# 	for j in range(0,len(k_buckets[i])):
	# 		if(k_buckets[i][j].id^target_id)==dis:
	# 			closest_nodes.nodes.append(k_buckets[i][j])
	# 			count+=1
	# 			if count==k:
	# 				break
	# 		dis+=1
	# 	if count==k:
	# 		break
	# print("hello,closese now!")
	#closest_nodes.responding_node=localnode
	# print("closest_nodes.responding_node is%d"%closest_nodes.responding_node.id)
	return closest_nodes



#in mode 0: remove to the tail
#in mode 1: not change the position
def update_bucket(k_buckets,update_node,localid,k,mode):
	distance=XOR(update_node.id,localid)
	layer=math.floor(math.log(distance,2))
	#print("the layer is %d"%layer)
	if len(k_buckets[layer]) >0:
		#("hello this is debug1!")
		found = 0
		for node in k_buckets[layer]:
			if node.id==update_node.id:
				found=1
				if mode == 0:
					k_buckets[layer].remove(node)
					k_buckets[layer].append(update_node)
					break
		if found==0:
			if len(k_buckets[layer])<k:
				k_buckets[layer].append(update_node)
			else:
				del(k_buckets[layer][0])
				k_buckets[layer].append(update_node)
	else:
		k_buckets[layer].append(update_node)
	# print("layer1:%d"%k_buckets[1][0].id)


class KadImplServicer(csci4220_hw3_pb2_grpc.KadImplServicer):

	def __init__(self,localnode,k):
		# global localnode
		# global k
		self.mynode=localnode
		#print("mynode is %d"%self.mynode.id)
		#self.k_buckets = []
		self.k=k
		#print("k is%d"%self.k)

	def FindNode(self, request, context):
		#
		# distance=self.mynode.id^request
		# search_bucket=math.floor(log(distance,2))
		# for i in range(0,len(self.k_buckets[search_bucket])):
		# 	if k_buckets[search_bucket][i].id == request :
		# 		return
		#search for myself?
		global k_buckets
		print("Serving FindNode(%d) request for %d"%(request.idkey,request.node.id))
		# if request.idkey==self.mynode.id :
		# 	update_bucket(k_buckets, request.node, self.mynode.id, self.k)
		# 	return self.mynode
		# else:
		# print(self.mynode.id)
		# print(request.idkey)
		#print_buckets()
		k_closest_nodes=find_k_closest(k_buckets,self.mynode,request.idkey,request.node.id,self.k)
		#print("the")
		update_bucket(k_buckets, request.node, self.mynode.id, self.k,0)
		#print_buckets()
		return k_closest_nodes


	def FindValue(self,request,context):
		global key_values
		global k_buckets
		print("Serving FindKey(%d) request for %d" % (request.idkey, request.node.id))
		#results=csci4220_hw3_pb2.KV_Node_Wrapper(responding_node=self.mynode)
		#results.responding_node=self.mynode
		update_bucket(k_buckets, request.node, self.mynode.id, self.k,0)
		value_found=key_values.get(request.idkey)
		if value_found is None:
			#nodelist=self.FindNode(request)
			k_closest_nodes = find_k_closest(k_buckets, self.mynode, request.idkey, request.node.id, self.k)
			# results.responding_node = self.mynode
			# results.mode_kv = False
			# results.nodes=k_closest_nodes.nodes
			return csci4220_hw3_pb2.KV_Node_Wrapper(responding_node=self.mynode,
													mode_kv=False,
													nodes=k_closest_nodes.nodes)
		else:
			# results.responding_node = self.mynode
			# results.mode_kv=True
			# results.kv=csci4220_hw3_pb2.KeyValue(node=self.mynode,key=request.idkey,value=value_found)
			keyvalue=csci4220_hw3_pb2.KeyValue(node=self.mynode,key=request.idkey,value=value_found)
			return csci4220_hw3_pb2.KV_Node_Wrapper(responding_node=self.mynode,
												mode_kv=True,
												kv=keyvalue)
		# return results


	def Store(self,request,context):
		global key_values
		global k_buckets
		key_values[request.key]=request.value
		print("Storing key %d value \"%s\""%(request.key,request.value))
		update_bucket(k_buckets,request.node,self.mynode.id,self.k,0)
		return csci4220_hw3_pb2.IDKey(node=self.mynode,idkey=request.key)


	def Quit(self,request,context):
		global k_buckets
		distance=XOR(request.idkey,self.mynode.id)
		layer = math.floor(math.log(distance, 2))
		for node in k_buckets[layer]:
			if node.id == request.idkey:
				k_buckets[layer].remove(node)
				print("Evicting quitting node %d from bucket %d"%(request.idkey,layer))
				return csci4220_hw3_pb2.IDKey(node=self.mynode,idkey=request.idkey)
		print("No record of quitting node %d in k-buckets."%request.idkey)
		return csci4220_hw3_pb2.IDKey(node=self.mynode)


#client work
def BootStrap(stub,localnode,k):
	global k_buckets
	results=stub.FindNode(csci4220_hw3_pb2.IDKey(node=localnode,idkey=localnode.id))
	update_bucket(k_buckets,results.responding_node,localnode.id,k,0)
	for node in results.nodes:
		update_bucket(k_buckets,node,localnode.id,k,0)

	#printing
	print("After BOOTSTRAP(%d), k_buckets now look like:"%results.responding_node.id)
	print_buckets( )


def Find_Node(targetid,k_buckets,localnode,k):
	visited_node=[]
	idkey=csci4220_hw3_pb2.IDKey(node=localnode,idkey=targetid)
	if targetid == localnode.id :
		print("Found destination id %d" % targetid)
		return

	while(1):
		uncontacted_node = []
		#closest_found = sort_buckets(k_buckets)
		closest_found=find_k_closest(k_buckets,localnode,targetid,localnode.id,k)
		for node in closest_found.nodes:
			visited=0
			for v in visited_node:
				if node.id == v.id:
					visited = 1
				if node.id == localnode.id:
					visited = 1
			if visited==0 :
				uncontacted_node.append(node)
		if len(uncontacted_node) ==0:
			print("Could not find destination id %d"%targetid)
			return
		else:
			for node in uncontacted_node:
				if node.id == targetid :
					print("Found destination id %d"%targetid)
					return
				visited_node.append(node)
				remote_addr = node.address
				remote_port = node.port
				# remote_addr_string=command[1]
				# remote_port_string = command[2]
				# remote_addr = socket.gethostbyname(remote_addr_string)
			# channel = grpc.insecure_channel(remote_addr + ':' + str(remote_port))
				results=csci4220_hw3_pb2.NodeList()
				with grpc.insecure_channel(remote_addr + ':' + str(remote_port)) as channel:
					stub = csci4220_hw3_pb2_grpc.KadImplStub(channel)
					results=stub.FindNode(idkey)
				channel.close()
				update_bucket(k_buckets,node,localnode.id,k,0)
				for r in results.nodes:
					update_bucket(k_buckets,r,localnode.id,k,1)



def store(keyvaluepair,localnode):
	#sorted_nodes=find_k_closest(k_buckets,localnode,key,localnode.id,k)
	global k_buckets
	sorted_nodes=[]
	sorted_nodes.append(localnode)
	for node_list in k_buckets:
		for node in node_list:
			sorted_nodes.append(node)
	sorted_nodes.sort(key=lambda x: XOR(keyvaluepair.key, x.id))
	target_node=sorted_nodes[0]
	if target_node.id==localnode.id:
		global key_values
		key_values[keyvaluepair.key] = keyvaluepair.value
		# print("Storing key %d value \"%s\"" % (keyvaluepair.key, keyvaluepair.value))
	else:
		remote_addr = target_node.address
		remote_port = target_node.port
		with grpc.insecure_channel(remote_addr + ':' + str(remote_port)) as channel:
			stub = csci4220_hw3_pb2_grpc.KadImplStub(channel)
			results = stub.Store(keyvaluepair)
		channel.close()
	print("Storing key %d at node %d"%(keyvaluepair.key,target_node.id))
	#update_bucket(k_buckets,target_node, localnode.id, k)


def Find_Value(targetkey,k_buckets,localnode,k):
	global key_values
	visited_node = []
	idkey = csci4220_hw3_pb2.IDKey(node=localnode, idkey=targetkey)
	# if targetid == localnode.id:
	# 	print("Found destination id %d" % targetid)
	# 	return
	value_found = key_values.get(targetkey)
	if value_found is not None:
		print("Found data \"%s\" for key %d" % (value_found, targetkey))
		return
	else:
		while (1):
			uncontacted_node = []
			# closest_found = sort_buckets(k_buckets)
			closest_found = find_k_closest(k_buckets, localnode, targetkey, localnode.id, k)
			for node in closest_found.nodes:
				visited = 0
				for v in visited_node:
					if node.id == v.id:
						visited = 1
					if node.id == localnode.id:
						visited = 1
				if visited == 0:
					uncontacted_node.append(node)
			if len(uncontacted_node) == 0:
				print("Could not find key %d" % targetkey)
				return
			else:
				for node in uncontacted_node:
					# if node.id == targetid:
					# 	print("Found destination id %d" % targetid)
					# 	return
					visited_node.append(node)
					remote_addr = node.address
					remote_port = node.port
				# remote_addr_string=command[1]
				# remote_port_string = command[2]
				# remote_addr = socket.gethostbyname(remote_addr_string)
				# channel = grpc.insecure_channel(remote_addr + ':' + str(remote_port))
					results = csci4220_hw3_pb2.KV_Node_Wrapper()
					with grpc.insecure_channel(remote_addr + ':' + str(remote_port)) as channel:
						stub = csci4220_hw3_pb2_grpc.KadImplStub(channel)
						results = stub.FindValue(idkey)
					channel.close()
					update_bucket(k_buckets, node, localnode.id, k,0)
					# for r in results.nodes:
					# 	update_bucket(k_buckets, r, localnode.id, k)
					if results.mode_kv is True:
						value_found=results.kv.value
						print("Found value \"%s\" for key %d"%(value_found,targetkey))
						return
					else:
						node_list=results.nodes
						for i in node_list:
							update_bucket(k_buckets,i,localnode.id,k,1)


def quit(k_buckets,localnode,k):
	request=csci4220_hw3_pb2.IDKey(node=localnode,idkey=localnode.id)
	for layer in k_buckets:
		if len(layer) > 0:
			for node in layer:
				print("Letting %d know I'm quitting."%node.id)
				remote_addr = node.address
				remote_port = node.port
				with grpc.insecure_channel(remote_addr + ':' + str(remote_port)) as channel:
					stub = csci4220_hw3_pb2_grpc.KadImplStub(channel)
					results = stub.Quit(request)
				channel.close()
				#layer.remove(node)
	print("Shut down node %d"%localnode.id)

def run():
	if len(sys.argv) != 4:
		print("Error, correct usage is {} [my id] [my port] [k]".format(sys.argv[0]))
		sys.exit(-1)

	local_id = int(sys.argv[1])
	my_port = str(int(sys.argv[2])) # add_insecure_port() will want a string
	k = int(sys.argv[3])
	my_hostname = socket.gethostname() # Gets my host name
	my_address = socket.gethostbyname(my_hostname) # Gets my IP address from my hostname
	#my_address = socket.gethostbyname("localhost")
	localnode=csci4220_hw3_pb2.Node(id=local_id,port=int(my_port),address=my_address)
	global k_buckets
	#initialize
	for i in range(0,4):
		list = []
		k_buckets.append(list)

	''' Use the following code to convert a hostname to an IP and start a channel
	Note that every stub needs a channel attached to it
	When you are done with a channel you should call .close() on the channel.
	Submitty may kill your program if you have too many file descriptors open
	at the same time. '''
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
	csci4220_hw3_pb2_grpc.add_KadImplServicer_to_server(
		KadImplServicer(localnode,k), server)
	server.add_insecure_port(my_hostname+':'+my_port)
	#server.add_insecure_port("localhost"+ ':' + my_port)
	server.start()
	#for debug
	#print("hello, the server starts!\n")
	while(1):
		command=sys.stdin.readline()
		#split the command
		command=command.split()
		if command[0]=="BOOTSTRAP":
			remote_addr_string=command[1]
			remote_port_string=command[2]
			remote_addr = socket.gethostbyname(remote_addr_string)
			#remote_addr = socket.gethostbyname("localhost")
			remote_port = int(remote_port_string)
			#channel = grpc.insecure_channel(remote_addr + ':' + str(remote_port))
			with grpc.insecure_channel(remote_addr + ':' + str(remote_port)) as channel:
				stub = csci4220_hw3_pb2_grpc.KadImplStub(channel)
				BootStrap(stub,localnode,k)
			channel.close()
		if command[0]=="FIND_NODE":
			nodeID=int(command[1])
			print("Before FIND_NODE command, k-buckets are:")
			print_buckets()
			Find_Node(nodeID,k_buckets,localnode,k)
			print("After FIND_NODE command, k-buckets are:")
			print_buckets()
		if command[0]=="STORE":
			keyid=int(command[1])
			value_store=command[2]
			key_value= csci4220_hw3_pb2.KeyValue(node=localnode, key=keyid,value=value_store)
			store(key_value,localnode)
		if command[0]=="FIND_VALUE":
			key_id=int(command[1])
			print("Before FIND_VALUE command, k-buckets are:")
			print_buckets()
			Find_Value(key_id, k_buckets, localnode, k)
			print("After FIND_VALUE command, k-buckets are:")
			print_buckets()
		if command[0]=="QUIT":
			quit(k_buckets,localnode,k)
			return

	server.wait_for_termination()




if __name__ == '__main__':
	run()
