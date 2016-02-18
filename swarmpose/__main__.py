""" main code goes here """
from docker import Client
import argparse
import yaml

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
		self.yaml_dict = self.parseFile(yamal)
		#generate a dictionary of nodes with no dependancies
		self.starting_nodes = {name:config for name,config in self.yaml_dict.items() if 'links' not in config}
		print (self.starting_nodes)
		for image in self.starting_nodes:
			self.runImage(image)

	#parse the yamal file and return a dictionary
	def parseFile(self, file):
		with open(file, 'r') as fh:
			yaml_dict=yaml.load(fh)
			print (yaml_dict)
			return yaml_dict

	def runImage(self, image):
		#Run the hello-world image and print the output
		container = self.cli.create_container(image=image)
		self.cli.start(container=container.get('Id'))

		print (self.cli.logs(container=container.get('Id')).decode('UTF-8'))
		result = self.cli.inspect_container(container=container.get('Id'))

		print ("This image ran on " + result['Node']['Addr'])


if __name__ == '__main__':
	args = clargs()
	mySwarmpose= Swarmpose(args.config)

