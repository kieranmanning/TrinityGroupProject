from docker import Client
import argparse
import yaml
import pprint

#allows us to specify the command line arguments that the script must recieve in order to execute
def clargs():
	parser = argparse.ArgumentParser(description='a script to start an application on a distributed swarm network')
	required = parser.add_argument_group('required arguments')
	sub_parser = parser.add_subparsers(dest='action')
	#sub commands for the program
	parser_start = sub_parser.add_parser('start', help='start an application')
	parser_stop = sub_parser.add_parser('stop', help='stop an application')
	parser_stop = sub_parser.add_parser('cc', help='clear all containers from swarm')
	# required arguments
	required.add_argument('-c', '--config', required=True, help='yaml file describing the application')
	#optional arguments
	parser.add_argument('-q', '--quiet', help='Supress messages from the script')
	parser.add_argument('-n', '--network', help='Name of the overlay network')
	return parser.parse_args()

class Swarmpose():
	def createOverlayNetwork(self, name):
		self.cli.create_network(name=name, driver="overlay")

	def networkExists(self, network):
		networks = self.cli.networks(names=[network])
		return (len(networks) != 0)

	#initialise the swarmpose class
	def __init__(self, yamal, network="dockernet"):
		self.yamal = yamal
		self.HOST = "178.62.11.78"
		self.PORT = "993"
		#Connect to remote daemon
		self.cli = Client(base_url='tcp://' + self.HOST + ':' + self.PORT)
		#parse the yaml file into a dictionary of dictionaries
		self.nodes = self.parseFile(yamal)
		self.network = network
		if (self.networkExists(network) != True):
			self.createOverlayNetwork(network)

	#parse the yamal file and return a dictionary
	def parseFile(self, file):
		with open(file, 'r') as fh:
			nodes=yaml.load(fh)
			return nodes

	def killAllTheContainers(self):
		#don't look back!
		for name,val in self.nodes.items():
			print ("Purging " + name + "...")
			self.cli.remove_container(name, force=True)

	def runImage(self, name, image, ports, links=None):
		container = self.cli.create_container(image=image, ports=ports, name=name, host_config=self.cli.create_host_config(network_mode=self.network))
		self.cli.start(container=container.get('Id'))
		result = self.cli.inspect_container(container=container.get('Id'))
		print ("Started " + name + " on " + result['Node']['Addr'])
		return container.get('Id')

	def stopImage(self, container):
		print("Stopping image "+ container)
		self.cli.stop(container)

	def start(self):
		print('**** Starting Application on Swarm ****')
		#seperate our nodes into two dictionaries, the starting_nodes wich have no dependancies and
		#remaining nodes which have dependancies
		starting_nodes = {name:config for name,config in self.nodes.items() if 'links' not in config}
		remaining_nodes = {name:self.nodes[name] for name  in self.nodes.keys() if name not in starting_nodes.keys()}

		#Create a dictionary to indcate the nodes that have been started
		nodes_run = {}
		for name in starting_nodes:
			test = self.runImage(name, self.nodes[name]['image'], self.nodes[name]['expose'])
		nodes_run.update(starting_nodes)
		#keep runnng until all nodes have been run
		while len(nodes_run) != len(self.nodes):
			#get the next dictionary of nodes that depend on the starting nodes
			next_nodes_2run = self.nextNodesRunning(remaining_nodes, nodes_run)
			for name in next_nodes_2run:
				test = self.runImage(name, self.nodes[name]['image'], self.nodes[name]['expose'], self.nodes[name]['links'])
			nodes_run.update(next_nodes_2run)
			remaining_nodes = {name:self.nodes[name] for name in self.nodes.keys() if name not in nodes_run.keys()}

	def stop(self):
		print('**** Stopping Application ****')
		can_stop=True
		nodes_stopped={}
		while(len(nodes_stopped)!=len(self.nodes)):
			for temp, config in self.nodes.items():
				for name, values in self.nodes.items():
					if(temp in 'links') :
						if(inspect_container(name)):
							can_stop=False
				if(can_stop == True and temp not in nodes_stopped):
					nodes_stopped[temp] = config
					self.stopImage(temp)



	def nextNodesRunning(self, remaining_nodes, nodes_ran):
		#get the next dictionary of nodes that depend on the starting nodes
		next_nodes_run = {}
		for name, config in remaining_nodes.items():
			if set(config['links']).issubset(set(list(nodes_ran.keys()))):
				next_nodes_run[name] = config
				return next_nodes_run

if __name__ == '__main__':
	args = clargs()
	print(args.action)
	mySwarmpose= Swarmpose(args.config, args.network)
	if(args.action == 'start'):
		mySwarmpose.start()
	elif(args.action == 'cc'):
		mySwarmpose.killAllTheContainers()
	else:
		mySwarmpose.stop()
