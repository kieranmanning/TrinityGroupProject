""" main code goes here """
from docker import Client
import argparse
import yaml

def clargs():
	parser = argparse.ArgumentParser(description='a script to start an application on a distributed system')
	requiredNamed = parser.add_argument_group('required named arguments')
	#required arguments
	requiredNamed.add_argument('-c', '--config', required=True, help='config file describing the application')
	return parser.parse_args()


class Swarmpose():

	def __init__(self, yamal):
		self.yamal = yamal
		self.HOST = "51.255.33.85"
		self.PORT = "443" #443 redirected to port 4000 on remote server

		#Connect to remote daemon
		self.cli = Client(base_url='tcp://' + self.HOST + ':' + self.PORT)
		# print (cli.info())

		#Run the hello-world image and print the output
		self.container = self.cli.create_container(image='hello-world:latest')
		self.cli.start(container=self.container.get('Id'))

		print (self.cli.logs(container=self.container.get('Id')).decode('UTF-8'))
		result = self.cli.inspect_container(container=self.container.get('Id'))

		print ("This image ran on " + result['Node']['Addr'])

		self.parseFile('env.yml')

	def parseFile(self, file):
		with open(file, 'r') as fh:
			yaml_dict=yaml.load(fh)
			print (yaml_dict)
			return yaml_dict

	def searchForStart(self, dockerNodes):
		return [img for img in dockerNodes if img['links'] == '']



if __name__ == '__main__':
	args = clargs()
	mySwarmpose= Swarmpose(args.config)

