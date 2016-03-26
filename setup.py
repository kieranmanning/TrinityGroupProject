from distutils.core import setup

install_requires =[
  'docker-py'
  'argparse'
  'pyyaml'
]

setup(
      name="swarmpose",
      version="1.0",
      author="""Ciaran Costello,
                Marijan Gradecak,
                Laura Rundle,
                Cal Martin,
                Niall Wall
                Dervla Walsh""",
      author_email="costeloci@tcd.ie",
      packages=['swarmpose',],
      url="",
      description="a Docker Compose like script to start multi-tiered applications on a Docker Swarm"
      )