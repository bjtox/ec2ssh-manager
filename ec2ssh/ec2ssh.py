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

class Connector:
  def __init__(self, region, profile, port):
    self.hosts_folder = expanduser("~")
    self.directory_to_save = self.hosts_folder+'/.ec2ssh/hosts/'
    self.region_name = region
    if self.region_name != None:  
      self.port = port
      self.profile = profile
      if profile!=None:
        self.session = boto3.Session(profile_name=self.profile)
        self.client = self.session.client('ec2',region_name=self.region_name)
      else:
        self.client = boto3.client('ec2',region_name=self.region_name)

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
      sys.exit("File Host doesn't exist")

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

  def addConfig(self,args):
    config = configparser.ConfigParser()
    self.printMenu()
    valid_choise=0
    usr_input = ''
    while usr_input not in ['1', '2', '3']:
      if valid_choise :
        print("Not Valid Choise")
      valid_choise=1
      usr_input = input("Input: ")

    if usr_input == "1":
      config['Connection']= {}
      config['Connection']['type'] = "direct"
      config['EC2INSTANCE'] = {}
      config['EC2INSTANCE']['pem_path'] = input('Enter a keyPair EC2 file path (absolute path):\n-> ')
      config['EC2INSTANCE']['user'] = input('Enter a EC2 user (default "ec2-user"):\n-> ')
      config['EC2INSTANCE']['ec2_instance_id'] = input('Enter a EC2 Instance ID:\n-> ')
      if not config['EC2INSTANCE']['user']:
        config['EC2INSTANCE']['user'] = 'ec2-user'
    elif usr_input == "2":
      config['Connection']= {}
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
      config['Connection']= {}
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
    with open(self.directory_to_save+args[2]+'.ini', 'w') as configfile:
      config.write(configfile)
    print("File Config "+args[2]+" created")

  def direct_connect(self,ec2_instance_config):
    target = {'key': ec2_instance_config['pem_path'], 'user': ec2_instance_config['user'], 'host': ec2_instance_config['ec2_instance_id']}
    target_ec2 = self.client
    target_response = target_ec2.describe_instances(InstanceIds=[target['host']])
    target_ip = target_response['Reservations'][0]['Instances'][0]['PublicIpAddress']
    print(target_ip)
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

  def ec2ssh(self,args):
    config = self.read_config(args[2])
    if config['Connection']['type'] == "direct":
      self.direct_connect(config['EC2INSTANCE'])
    elif config['Connection']['type'] == "bastion":
      self.bastion_connect(config['EC2INSTANCE'], config['BASTIONHOST'])
    elif config['Connection']['type'] == "asg":
      print ('Please select an option:')
      i=1
      selects = {}
      for instance in self.list_instance_in_asg(config['ASG']['name']):
        print ("   "+str(i)+". "+instance['InstanceId'])
        selects[i]=instance['InstanceId']
        i+=1
      config_asg = {}
      choise = input('Enter Value: ')
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

  def list_avaible_connection(self,args):
    print (30 * '-')
    for file in os.listdir(self.directory_to_save):
      if file.endswith(".ini"):
          name_file = file.replace('.ini','')
          print(" File Name: "+name_file)
          config = self.read_config(name_file)
          print(" Type: "+config['Connection']['type'])
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


  def rm_connecition(self,args):
    try:
      os.remove(self.directory_to_save+args[2]+'.ini')
      print(args[2]+" connection was removed!")
    except OSError:
      print(args[2]+" connection doesn't exist!")
      pass

  def main(self,args):
    if not os.path.exists(self.directory_to_save):
      os.makedirs(directory_to_save)
    args = sys.argv
    switcher = {
      "add":self.addConfig,
      "connect": self.ec2ssh,
      "ls": self.list_avaible_connection,
      "rm": self.rm_connecition
    }
    return switcher[args[1]](args)