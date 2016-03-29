from docker import Client
from docker import errors
import argparse
import yaml

def sharedFlags(subparser):
	required = subparser.add_argument_group('required arguments')
	required.add_argument('-c', '--config', required=True, help='yaml file describing the application')
	required.add_argument('-m', '--manager', required=True, help='sepcify the host and port of the docker manager eg 127.0.0.1:3000')
	subparser.add_argument('-q', '--quiet', required=False, help='Supress messages from the script')

#allows us to specify the command line arguments that the script must recieve in order to execute
def clargs():
	main_parser = argparse.ArgumentParser(description='a script to start an application on a distributed swarm network')
	# required = parser.add_argument_group('required arguments')
	sub_parser = main_parser.add_subparsers(dest='cmd')
	sub_parser.required = True
	#sub commands for the program
	start = sub_parser.add_parser('start', help='start an application')
	sharedFlags(start)
	stop = sub_parser.add_parser('stop', help='stop an application')
	sharedFlags(stop)
	purge = sub_parser.add_parser('purge', help='clear all containers specified in the config file from swarm')
	sharedFlags(purge)
	create = sub_parser.add_parser('create', help='create containers on the swarm')
	create.add_argument('-n', '--network', help='Name of the overlay network, if none specified default name (\'dockernet\') will be used', default='dockernet')
	sharedFlags(create)

	return main_parser.parse_args()

class Swarmpose():
	#initialise the swarmpose class
	def __init__(self, yamal, manager, network="dockernet"):
		self.HOST, self.PORT = manager.split(':')
		#Connect to remote daemon
		self.cli = Client(base_url='tcp://' + self.HOST + ':' + self.PORT)
		#parse the yaml file into a dictionary of dictionaries
		self.nodes = self.parseConfig(yamal)
		#check if an overlay network exists if not create one (default='Dockernet')
		self.network = network
		if (self.networkExists(network) != True):
			self.createOverlayNetwork(network)

	def createOverlayNetwork(self, name):
		self.cli.create_network(name=name, driver="overlay")

	def networkExists(self, network):
		networks = self.cli.networks(names=[network])
		return (len(networks) != 0)

	#parse the yamal file and return a dictionary
	def parseConfig(self, file):
		with open(file, 'r') as fh:
			nodes=yaml.load(fh)
			return nodes

	#removes all containers (in no particular order) from the swarm
	def removeAllContainers(self):
		#don't look back!
	  print("**** Clearing Containers ****")
	  for name,val in self.nodes.items():
	    try:
	      print("Purging %s ..." % name)
	      self.cli.remove_container(name, force=True)
	    except errors.NotFound as e:
	      print(e.explanation.decode('UTF-8'))

	#create containers on the swarm
	def createContainers(self):
		for name, config in self.nodes.items():
			try:
				expose = None
				if ('ports' in config):
					expose = dict(item.split(':') for item in self.nodes[name]['ports'])
				container = self.cli.create_container(image=config['image'] , ports=config['expose'], name=name, host_config=self.cli.create_host_config(port_bindings=expose, network_mode=self.network))
				result = self.cli.inspect_container(container=name)
				print("Created %s container on node %s" % (name, result['Node']['Addr']))
				if (expose is not None):
					print ("Will expose ports " + str(expose) + " on " + result['Node']['Addr'])
			except errors.APIError as e:
				print(e.explanation.decode('UTF-8'))

	#run the image with the given name
	def runImage(self, name):
		try:
			self.cli.start(container=name)
			result = self.cli.inspect_container(container=name)
			print('Container %s started on node %s' % (name, result['Node']['Addr']))
		except errors.APIError as e:
			print(e.explanation.decode('UTF-8'))

	#start the application described by config file in dependancy order
	def start(self):
		print('**** Starting Application on Swarm ****')
		dependancy_list = self.genDependancyList()
		for name in dependancy_list:
			self.runImage(name)

	#stop images (from the config file) currently running on swarm in reverse dependancy order
	def stopImage(self, container):
		try:
			print("Stopping image "+ container)
			self.cli.stop(container)
		except errors.APIError as e:
				print(e.explanation.decode('UTF-8'))

	#stop the application described by config file
	def stop(self):
		print("**** Stopping Application *****")
		depend_list = self.genDependancyList()
		for name in reversed(depend_list):
			self.stopImage(name)

	def genDependancyList(self):
		#find nodes with no dependancies
		starting_nodes = {name:config for name,config in self.nodes.items() if 'links' not in config}
		#find nodes with dependancies
		remaining_nodes = {name:self.nodes[name] for name  in self.nodes.keys() if name not in starting_nodes.keys()}
		dependancy_list = list(starting_nodes.keys())
		while len(remaining_nodes) > 0:
			nextNode = self.nextNodeRunning(remaining_nodes, starting_nodes)
			dependancy_list.append(nextNode)
			remaining_nodes.pop(nextNode, None)
			starting_nodes[nextNode] = self.nodes[nextNode]
		return dependancy_list

	#returns the name of the node which can be started next
	#this is based on the remaining nodes and the nodes that have been started
	def nextNodeRunning(self, remaining_nodes, nodes_ran):
		for name, config in remaining_nodes.items():
			#if a nodes links are a subset of the nodes ran (dependancies have been fullfiled)
			if set(config['links']).issubset(set(list(nodes_ran.keys()))):
				return name

if __name__ == '__main__':
	args = clargs()
	if(args.cmd == 'start'):
		Swarmpose(args.config, args.manager).start()
	elif(args.cmd == 'purge'):
		Swarmpose(args.config, args.manager).removeAllContainers()
	elif(args.cmd == 'create'):
		Swarmpose(args.config, args.manager, args.network).createContainers()
	else:
		#args.cmd == stop
		Swarmpose(args.config, args.manager).stop()
