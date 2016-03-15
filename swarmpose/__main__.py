""" main code goes here """
from docker import Client
import argparse
import yaml
import pprint

#allows us to specify the command line arguments that the script must recieve in order to execute
def clargs():
	parser = argparse.ArgumentParser(description='a script to start an application on a distributed system')
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
	return parser.parse_args()


class Swarmpose():
	#initialise the swarmpose class
	def __init__(self, yamal):
		self.yamal = yamal
		self.HOST = "178.62.11.78"
		self.PORT = "443"
		#Connect to remote daemon
		self.cli = Client(base_url='tcp://' + self.HOST + ':' + self.PORT)
		#parse the yaml file into a dictionary of dictionaries
		self.nodes = self.parseFile(yamal)
		#self.nodes_run.update(self.starting_nodes)

		#self.next_nodes_2run = {key:val for key, val in self.yamal_dict.items() if self.starting_nodes.has_key()}

	#parse the yamal file and return a dictionary
	def parseFile(self, file):
		with open(file, 'r') as fh:
			nodes=yaml.load(fh)
			print (nodes)
			return nodes

	def killAllTheContainers(self):
		#don't look back!
		toRemove = self.cli.containers(all='true')
		for container in toRemove:
			for name in self.nodes:
				if ''.join(container['Names']).find(name):
					self.cli.remove_container(container['Id'], force=True)

	def runImage(self, name, image, ports, links=None):
		#Run the hello-world image and print the output
		if (links != None):
			toLink = dict(zip(links, links))
			print (toLink)
			container = self.cli.create_container(image=image, ports=ports, name=name, host_config=self.cli.create_host_config(network_mode="dockernet"))
			self.cli.connect_container_to_network(container=container.get('Id'), net_id="dockernet")
			self.cli.start(container=container.get('Id'))
		else:
			container = self.cli.create_container(image=image, ports=ports, name=name, host_config=self.cli.create_host_config(network_mode="dockernet"))
			self.cli.connect_container_to_network(container=container.get('Id'), net_id="dockernet")
			self.cli.start(container=container.get('Id'))

		print (self.cli.logs(container=container.get('Id')).decode('UTF-8'))
		result = self.cli.inspect_container(container=container.get('Id'))

		print (result)
		print ("This image ran on " + result['Node']['Addr'])
		return container.get('Id')

	def stopImage(self, container):
		self.cli.stop(container)

	def start(self):
		print('**** Starting Application ****')
		#seperate our nodes into two dictionaries, the starting_nodes wich have no dependancies and
		#remaining nodes which have dependancies
		starting_nodes = {name:config for name,config in self.nodes.items() if 'links' not in config}
		remaining_nodes = {name:self.nodes[name] for name  in self.nodes.keys() if name not in starting_nodes.keys()}

		#Create a dictionary to indcate the nodes that have been started
		nodes_run = {}
		for name in starting_nodes:
			test = self.runImage(name, self.nodes[name]['image'], self.nodes[name]['expose'])
			#self.stopImage(test)
		nodes_run.update(starting_nodes)
		#keep runnng until all nodes have been run
		while len(nodes_run) != len(self.nodes):
			#get the next dictionary of nodes that depend on the starting nodes
			next_nodes_2run = self.nextNodesRunning(remaining_nodes, nodes_run)
			print ("remaining nodes: %s" % remaining_nodes)
			print("starting next %s" % next_nodes_2run)
			for name in next_nodes_2run:
				test = self.runImage(name, self.nodes[name]['image'], self.nodes[name]['expose'], self.nodes[name]['links'])
				#self.stopImage(test)
			nodes_run.update(next_nodes_2run)
			remaining_nodes = {name:self.nodes[name] for name in self.nodes.keys() if name not in nodes_run.keys()}



	def stop(self):
		print('**** Stopping Application ****')
			#nodes_to_kill =[]
		can_stop=True
		nodes_stopped={}
#   starting_nodes = {name:config for name,config in self.nodes.items() if name not in 'links'}
		while(len(nodes_stopped)!=len(self.nodes)):
			for temp, config in self.nodes.items():

				for name, values in self.nodes.items():
					if(temp in 'links'):
						if(inspect_container(name)):
							can_stop=False
			if(can_stop == True):
				nodes_stopped[temp] = config
				stopImage(temp)



	def nextNodesRunning(self, remaining_nodes, nodes_ran):
		#get the next dictionary of nodes that depend on the starting nodes
		next_nodes_run = {}
		for name, config in remaining_nodes.items():
			if set(config['links']).issubset(set(list(nodes_ran.keys()))):
				next_nodes_run[name] = config

		#self.next_nodes_2run = {name:config for name, config in self.remaining_nodes.items() if set(config['links']).issubset(set(list(self.starting_nodes.keys())))}
		return next_nodes_run

if __name__ == '__main__':
	args = clargs()
	print(args.action)
	mySwarmpose= Swarmpose(args.config)
	if(args.action == 'start'):
		mySwarmpose.start()
	elif(args.action == 'cc'):
		mySwarmpose.killAllTheContainers()
	else:
		mySwarmpose.stop()
