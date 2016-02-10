""" main code goes here """
from docker import Client

def main():
	HOST = "51.255.33.85"
	PORT = "443" #443 redirected to port 4000 on remote server

	cli = Client(base_url='tcp://' + HOST + ':' + PORT)
	print cli.info()
  	pass








if __name__ == '__main__':
	main()