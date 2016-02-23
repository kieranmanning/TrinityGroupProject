""" main code goes here """
from docker import Client
import argparse
import yaml
import pprint

#allows us to specify the arguments that the script must recieve in order to execute
def clargs():
	parser = argparse.ArgumentParser(description='a script to start an application on a distributed system')
	required = parser.add_argument_group('required arguments')
	#required arguments
	required.add_argument('-c', '--config', required=True, help='yaml file describing the application')
	#optional arguments
	parser.add_argument('-q', '--quiet', help='Supress messages from the script')
	return parser.parse_args()


class Swarmpose():

	#initialise the swarmpose class
	def __init__(self, yamal):
		self.yamal = yamal
		self.HOST = "51.255.33.85"
		self.PORT = "443" #443 redirected to port 4000 on remote server
		#Connect to remote daemon
		self.cli = Client(base_url='tcp://' + self.HOST + ':' + self.PORT)
		#parse the yaml file into a dictionary of dictionaries
		self.nodes = self.parseFile(yamal)

		#seperate our nodes into two dictionaries, the starting_nodes wich have no dependancies and
		#remaining nodes which have dependancies
		self.starting_nodes = {name:config for name,config in self.nodes.items() if 'links' not in config}
		self.remaining_nodes = {name:self.nodes[name] for name  in self.nodes.keys() if name not in self.starting_nodes.keys()}

		#Create a dictionary to indcate the nodes that have been started
		self.nodes_run = {}
		for image in self.starting_nodes:
			 test = self.runImage(image, self.nodes[image]['expose'])
			 self.stopImage(test)
		self.nodes_run.update(self.starting_nodes)

		#get the next dictionary of nodes that depend on the starting nodes
		self.next_nodes_2run = {}
		for name, config in self.remaining_nodes.items():
			if set(config['links']).issubset(set(list(self.starting_nodes.keys()))):
				self.next_nodes_2run[name] = config

		# self.next_nodes_2run = {name:config for name, config in self.remaining_nodes.items() if set(config['links']).issubset(set(list(self.starting_nodes.keys())))}

		#self.nodes_run.update(self.starting_nodes)
		print("starting next %s" % self.next_nodes_2run)

		# self.next_nodes_2run = {key:val for key, val in self.yamal_dict.items() if self.starting_nodes.has_key()}

	#parse the yamal file and return a dictionary
	def parseFile(self, file):
		with open(file, 'r') as fh:
			nodes=yaml.load(fh)
			print (nodes)
			return nodes

	def runImage(self, image, ports):
		#Run the hello-world image and print the output
		bindings = dict(zip(ports, ports))
		print (bindings)
		container = self.cli.create_container(image=image, ports=ports, host_config=self.cli.create_host_config(port_bindings=bindings))
		self.cli.start(container=container.get('Id'))

		print (self.cli.logs(container=container.get('Id')).decode('UTF-8'))
		result = self.cli.inspect_container(container=container.get('Id'))

		print ("This image ran on " + result['Node']['Addr'])
		return container.get('Id')

	def stopImage(self, container):
		self.cli.stop(container)

if __name__ == '__main__':
	args = clargs()
	mySwarmpose= Swarmpose(args.config)

