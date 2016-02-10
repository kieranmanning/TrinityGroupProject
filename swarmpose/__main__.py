""" main code goes here """
from docker import Client
import pprint 

def main():
	HOST = "51.255.33.85"
	PORT = "443" #443 redirected to port 4000 on remote server

	#Connect to remote daemon
	cli = Client(base_url='tcp://' + HOST + ':' + PORT)
	#print cli.info()

	#Run the hello-world image and print the output
	container = cli.create_container(image='hello-world:latest')
	cli.start(container=container.get('Id'))

	pp = pprint.PrettyPrinter(indent=4)
	print cli.logs(container=container.get('Id'))
	result = cli.inspect_container(container=container.get('Id'))
	#pp.pprint(result)

	print "This image ran on " + result['Node']['Addr']
  	pass








if __name__ == '__main__':
	main()