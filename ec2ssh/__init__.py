from ec2ssh import ec2ssh
import sys, getopt
from optparse import OptionParser

def main():

  from optparse import OptionParser
  usage = "usage: %prog [command] [name] [options] arg1 arg2"+"\n"+"AWS configuration is REQUIRED"
  parser = OptionParser(usage)


  parser.add_option("-c", "--commands", dest="commands",action="store_true",
                      help="list all Commands", metavar="Commands")
  parser.add_option("-p", "--profile", dest="profile", default='default',
                    help="use Specific Profile", metavar="PROFILE_NAME")
  parser.add_option("-r", "--region", dest="region",
                    help="MANDATORY - use Specific Region", metavar="REGION_NAME")
  parser.add_option("-P", "--port",
                    dest="port", default='22',
                    help="Specify Port")

  (options, args) = parser.parse_args()

  if options.commands:   # if filename is not given
    print ("Command List:")
    print ("  add 'connection_name'        => to add a connection name")
    print ("  connect 'connection_name'    => connect to ec2")
    print ("  ls                           => to list avaible connections")
    print ("  rm 'connection_name'         => remove a connection")

  
  else:
    if sys.argv[1] == "connect":
      if not options.region:   # if filename is not given
        parser.error('Region not given')
    


    connector = ec2ssh.Connector(options.region, options.profile, options.port)
    connector.main(sys.argv)
    
