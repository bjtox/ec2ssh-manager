import subprocess
import boto3
import sys
import configparser
from codecs import open
from os.path import expanduser
import os
import glob
import inquirer
import argparse
import libtmux
import time

class Connector:
  def __init__(self, connection_name, profile):

    self.hosts_folder = expanduser("~")
    print(self.hosts_folder)
    self.profile = profile
    self.directory_to_save = self.hosts_folder+'/.ec2ssh/hosts/'
    if not os.path.exists(self.directory_to_save):
      os.makedirs(self.directory_to_save)

    
    if connection_name != None: 
      self.connection_name = connection_name
      self.config = self.read_config(connection_name)
      if self.config != False:
        self.port = self.config['Connection']['connection_port']
        self.region_name = self.config['Connection']['region']
        


  def open_tmux(self,selects,connection_name, region, profile, port):
    server = libtmux.Server()
    session = server.list_sessions()[0]
    print(session)
    
    window = session.new_window(attach=True, window_name=connection_name+str(round(time.time() * 1000)))

    instances = len(selects)
    print(instances)
    print(instances % 2 == 0)

    if instances % 2 == 0:
      count = 1
    else:
      count = 0

    while (count < instances):
       window.split_window()
       window.select_layout('tiled')
       count += 1

    selection = 1
    for pane in window.list_panes():
      pane.send_keys('ec2ssh connect -n {} -p {}'.format(connection_name,profile))
      pane.send_keys(str(selection))
      selection += 1
    
    window.set_window_option('synchronize-panes', True)


  def printMenu(self):
    print (30 * '-')
    print ("   M A I N - M E N U")
    print (30 * '-')
    print ("1. Direct Connect")
    print ("2. Pass from Bastion Host")
    print ("3. Autoscaling")
    print (30 * '-')

  def read_config(self,host):
    if os.path.isfile(self.directory_to_save+host+'.ini'):
      config = configparser.ConfigParser()
      config.sections()
      config.read(self.directory_to_save+host+'.ini')
      return(config);
    else:
      return False

  def query_yes_no(self,question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

  def addConfig(self):
    config = configparser.ConfigParser()
    self.printMenu()
    valid_choise=0
    usr_input = ''
    while usr_input not in ['1', '2', '3']:
      if valid_choise :
        print("Not Valid Choise")
      valid_choise=1
      usr_input = input("Input: ")

    config['Connection']= {}

    config['Connection']['region'] = input('Specify a Region:\n-> ')
    config['Connection']['connection_port'] = input('Specify a connection port (for direct or for Bastion):\n-> ')
    config['Connection']['profile'] = input('Specify which AWS profile use:\n-> ')
    if not config['Connection']['profile']:
        config['Connection']['profile'] = 'default'


    if usr_input == "1":
      config['Connection']['type'] = "direct"
      config['EC2INSTANCE'] = {}
      config['EC2INSTANCE']['pem_path'] = input('Enter a keyPair EC2 file path (absolute path):\n-> ')
      config['EC2INSTANCE']['user'] = input('Enter a EC2 user (default "ec2-user"):\n-> ')
      config['EC2INSTANCE']['ec2_instance_id'] = input('Enter a EC2 Instance ID:\n-> ')
      
      if not config['EC2INSTANCE']['user']:
        config['EC2INSTANCE']['user'] = 'ec2-user'

    elif usr_input == "2":
      config['Connection']['type'] = "bastion"
      config['EC2INSTANCE'] = {}
      config['EC2INSTANCE']['pem_path'] = input('Enter a keyPair EC2 file path (absolute path):\n-> ')
      config['EC2INSTANCE']['user'] = input('Enter a EC2 user (default "ec2-user"):\n-> ')
      config['EC2INSTANCE']['ec2_instance_id'] = input('Enter a EC2 Instance ID:\n-> ')
      config['BASTIONHOST'] = {}
      config['BASTIONHOST']['b_pem_path'] = input('Enter a Bastion pem file path (absolute path):\n-> ')
      config['BASTIONHOST']['b_user'] = input('Enter a Bastion user:\n-> ')
      config['BASTIONHOST']['b_ec2_instance_id'] = input('Enter a Bastion Instance ID:\n-> ')
      
      if not config['EC2INSTANCE']['user']:
        config['EC2INSTANCE']['user'] = 'ec2-user'
    
    elif usr_input == "3":
      config['Connection']['type'] = "asg"
      config['ASG'] = {}
      config['ASG']['pem_path'] = input('Enter a pem file path (absolute path):\n-> ')
      config['ASG']['user'] = input('Enter a user (default "ec2-user"):\n-> ')
      config['ASG']['name'] = input('Enter a ASG Name ID:\n-> ')

      if not config['ASG']['user']:
        config['ASG']['user'] = 'ec2-user'
      
      questions = self.query_yes_no("ASG allow ssh only from Bastion Host?")
      
      if questions == True:
        config['BASTIONHOST'] = {}
        config['BASTIONHOST']['b_pem_path'] = input('Enter a Bastion pem file path (absolute path):\n-> ')
        config['BASTIONHOST']['b_user'] = input('Enter a Bastion user:\n-> ')
        config['BASTIONHOST']['b_ec2_instance_id'] = input('Enter a Bastion Instance ID:\n-> ')
    
    with open(self.directory_to_save+self.connection_name+'.ini', 'w') as configfile:
      config.write(configfile)
    
    print("File Config "+self.connection_name+" created")

  def direct_connect(self,ec2_instance_config):
    target = {'key': ec2_instance_config['pem_path'], 'user': ec2_instance_config['user'], 'host': ec2_instance_config['ec2_instance_id']}
    target_ec2 = self.client
    target_response = target_ec2.describe_instances(InstanceIds=[target['host']])
    target_ip = target_response['Reservations'][0]['Instances'][0]['PublicIpAddress']
    subprocess.call("ssh-add {}".format(target['key']), shell=True)
    subprocess.call("ssh {}@{} -p {}".format(target['user'], target_ip, self.port), shell=True)

  def bastion_connect(self,ec2_instance_config,bastion_config):
    target = {'key': ec2_instance_config['pem_path'], 'user': ec2_instance_config['user'], 'host': ec2_instance_config['ec2_instance_id']}
    target_ec2 = self.client
    target_response = target_ec2.describe_instances(InstanceIds=[target['host']])
    bastion = {'key': bastion_config['b_pem_path'], 'user': bastion_config['b_user'], 'host': bastion_config['b_ec2_instance_id']}
    bastion_ec2 = self.client
    bastion_response = bastion_ec2.describe_instances(InstanceIds=[bastion['host']])
    bastion_ip = bastion_response['Reservations'][0]['Instances'][0]['PublicIpAddress']
    target_ip = target_response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['PrivateIpAddress']
    subprocess.call("ssh-add {} {}".format(bastion['key'], target['key']), shell=True)
    subprocess.call("ssh -t -A {}@{} -p {} ssh {}@{}".format(bastion['user'], bastion_ip,self.port, target['user'], target_ip), shell=True)

  def ec2ssh(self):
    self.session = boto3.Session(profile_name=self.profile)
    self.client = self.session.client('ec2',region_name=self.config['Connection']['region'])
    config = self.read_config(self.connection_name)
    
    if config['Connection']['type'] == "direct":
      self.direct_connect(config['EC2INSTANCE'])
    elif config['Connection']['type'] == "bastion":
      self.bastion_connect(config['EC2INSTANCE'], config['BASTIONHOST'])
    elif config['Connection']['type'] == "asg":
      print ('Please select an option:')
      print ("   0. All")
      i=1
      selects = {}
      for instance in self.list_instance_in_asg(config['ASG']['name']):
        print ("   "+str(i)+". "+instance['InstanceId']+" - "+instance['LifecycleState'])
        selects[i]=instance['InstanceId']
        i+=1

      config_asg = {}
      choise = input('Enter Value: ')

      if choise != "0":
        config_asg['pem_path']=config['ASG']['pem_path']
        config_asg['user']=config['ASG']['user']
        config_asg['ec2_instance_id']=selects[int(choise)]
        if config.has_section('BASTIONHOST'):
          config_asg_bastion = {}
          config_asg_bastion['b_pem_path']=config['BASTIONHOST']['b_pem_path']
          config_asg_bastion['b_user']=config['BASTIONHOST']['b_user']
          config_asg_bastion['b_ec2_instance_id']=config['BASTIONHOST']['b_ec2_instance_id']
          self.bastion_connect(config_asg, config_asg_bastion)
        else:
          self.direct_connect(config_asg)
      else:
        self.open_tmux(selects, self.connection_name, self.region_name, self.profile, self.port)
        

  def list_avaible_connection(self):
    print (30 * '-')
    
    for file in os.listdir(self.directory_to_save):
      if file.endswith(".ini"):
          name_file = file.replace('.ini','')
          print(" Connection Name: "+name_file)
          config = self.read_config(name_file)
          print(" Type: "+config['Connection']['type'])
          print(" Region Name: "+config['Connection']['region'])
          print(" Connection Port: "+config['Connection']['connection_port'])

          if config['Connection']['type'] == "direct":
            print(" Key Pair: "+config['EC2INSTANCE']['pem_path'])
            print(" User Pair: "+config['EC2INSTANCE']['user'])
            print(" Instance Id Pair: "+config['EC2INSTANCE']['ec2_instance_id'])
          elif config['Connection']['type'] == "bastion":
            print(" Key Pair: "+config['EC2INSTANCE']['pem_path'])
            print(" User Pair: "+config['EC2INSTANCE']['user'])
            print(" Instance Id Pair: "+config['EC2INSTANCE']['ec2_instance_id'])
            print(" Bastion Id: "+config['BASTIONHOST']['b_ec2_instance_id'])
          elif config['Connection']['type'] == "asg":
            print(" Key Pair: "+config['ASG']['pem_path'])
            print(" User Pair: "+config['ASG']['user'])
            print(" ASG Name: "+config['ASG']['name'])
            print(" Bastion Id: "+config['BASTIONHOST']['b_ec2_instance_id'])
      print (30 * '-')  

  def list_instance_in_asg(self, asg_name):
    if self.profile!=None:
      asg_client = self.session.client('autoscaling',region_name=self.region_name)
    else:
      asg_client = boto3.client('autoscaling',region_name=self.region_name)
    response = asg_client.describe_auto_scaling_groups(
      AutoScalingGroupNames=[
          asg_name,
      ]
    )
    return response['AutoScalingGroups'][0]['Instances']


  def rm_connecition(self):
    try:
      os.remove(self.directory_to_save+self.connection_name+'.ini')
      print(self.connection_name+" connection was removed!")
    except OSError:
      print(self.connection_name+" connection doesn't exist!")
      pass