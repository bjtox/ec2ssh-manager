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
  parser.add_option("-n", "--connection-name", dest="connection_name",
                    help="MANDATORY - use Specific connection name", metavar="CONNECTION_NAME")

  (options, args) = parser.parse_args()

  if options.commands:   # if filename is not given
    print ("Command List:")
    print ("  add -n 'connection_name'        => to add a connection name")
    print ("  connect -n 'connection_name'    => connect to ec2")
    print ("  ls                           => to list avaible connections")
    print ("  rm -n 'connection_name'         => remove a connection")

  
  else:
    if sys.argv[1] == "connect":
      if not options.connection_name:   # if filename is not given
        parser.error('Connection Name not given')
    
    connector = ec2ssh.Connector(options.connection_name, options.profile)

    
    args = sys.argv
    switcher = {
      "add":connector.addConfig,
      "connect": connector.ec2ssh,
      "ls": connector.list_avaible_connection,
      "rm": connector.rm_connecition
    }
    return switcher[args[1]]()