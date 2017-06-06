from ec2ssh import ec2ssh
import sys, getopt
from optparse import OptionParser

def main():

  from optparse import OptionParser
  usage = "usage: %prog [command] [name] [options] arg1 arg2"
  parser = OptionParser(usage)


  parser.add_option("-c", "--commands", dest="commands",action="store_false",
                      help="list all Commands", metavar="Commands")
  parser.add_option("-p", "--profile", dest="profile",
                    help="use Specific Profile", metavar="PROFILE")
  parser.add_option("-P", "--port",
                    dest="port", default='22',
                    help="Specify Port")

  (options, args) = parser.parse_args()

  connector = ec2ssh.Connector('eu-west-1', options.profile, options.port)
  connector.main(sys.argv)
