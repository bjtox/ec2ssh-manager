import subprocess
import boto3
import sys
import configparser
from codecs import open
from os.path import expanduser
import os
import glob

import argparse


class Connector:

  def __init__(self, region, profile, port):
    self.hosts_folder = expanduser("~")
    self.directory_to_save = self.hosts_folder+'/.ec2ssh/hosts/'
    self.region_name = region
    self.port = port
    if profile!=None:
      self.session = boto3.Session(profile_name=profile)
      self.client = self.session.client('ec2',region_name=self.region_name)
    else:
      self.client = boto3.client('ec2',region_name=self.region_name)

  

  def read_config(self,host):
    print(self.directory_to_save+host+'.ini')
    if os.path.isfile(self.directory_to_save+host+'.ini'):
      config = configparser.ConfigParser()
      config.sections()
      config.read(self.directory_to_save+host+'.ini')
      return(config);
    else:
      sys.exit("File Host doesn't exist")


  def addConfig(self,args):

    config = configparser.ConfigParser()
    self.printMenu()
    valid_choise=0
    usr_input = ''
    while usr_input not in ['1', '2']:
      if valid_choise :
        print("Not Valid Choise")
      valid_choise=1
      usr_input = input("Input: ")

    if usr_input == "1":
      config['EC2INSTANCE'] = {}
      config['EC2INSTANCE']['pem_path'] = input('Enter a pem file path (absolute path): ')
      config['EC2INSTANCE']['user'] = input('Enter a user (default "ec2-user"): ')
      config['EC2INSTANCE']['ec2_instance_id'] = input('Enter a Instance ID: ')
    elif usr_input == "2":
      config['EC2INSTANCE'] = {}
      config['EC2INSTANCE']['pem_path'] = input('Enter a pem file path (absolute path): ')
      config['EC2INSTANCE']['user'] = input('Enter a user (default "ec2-user"): ')
      config['EC2INSTANCE']['ec2_instance_id'] = input('Enter a Instance ID: ')
      config['BASTIONHOST'] = {}
      config['BASTIONHOST']['b_pem_path'] = input('Enter a Bastion pem file path (absolute path): ')
      config['BASTIONHOST']['b_user'] = input('Enter a Bastion user: ')
      config['BASTIONHOST']['b_ec2_instance_id'] = input('Enter a Bastion Instance ID: ')


    if not config['EC2INSTANCE']['user']:
        config['EC2INSTANCE']['user'] = 'ec2-user'

    with open(self.directory_to_save+args[2]+'.ini', 'w') as configfile:
      config.write(configfile)

    print("File Config "+args[2]+" created")

  def printMenu(self):
    print (30 * '-')
    print ("   M A I N - M E N U")
    print (30 * '-')
    print ("1. Direct Connect")
    print ("2. Pass from Bastion Host")
    print (30 * '-')

  def ec2ssh(self,args):

    config = self.read_config(args[2])
    target = {'key': config['EC2INSTANCE']['pem_path'], 'user': config['EC2INSTANCE']['user'], 'host': config['EC2INSTANCE']['ec2_instance_id']}
    target_ec2 = self.client
    target_response = target_ec2.describe_instances(InstanceIds=[target['host']])


    if config.has_section('BASTIONHOST'):
      bastion = {'key': config['BASTIONHOST']['b_pem_path'], 'user': config['BASTIONHOST']['b_user'], 'host': config['BASTIONHOST']['b_ec2_instance_id']}
      bastion_ec2 = self.client
      bastion_response = bastion_ec2.describe_instances(InstanceIds=[bastion['host']])
      bastion_ip = bastion_response['Reservations'][0]['Instances'][0]['PublicIpAddress']

      target_ip = target_response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['PrivateIpAddress']

      subprocess.call("ssh-add {} {}".format(bastion['key'], target['key']), shell=True)
      subprocess.call("ssh -t -A {}@{} ssh {}@{}".format(bastion['user'], bastion_ip, target['user'], target_ip), shell=True)

    else:
      target_ip = target_response['Reservations'][0]['Instances'][0]['PublicIpAddress']
      print(target_ip)
      subprocess.call("ssh-add {}".format(target['key']), shell=True)
      subprocess.call("ssh {}@{} -p {}".format(target['user'], target_ip, self.port), shell=True)

  def list_avaible_connection(self,args):
    print (30 * '-')
    for file in os.listdir(self.directory_to_save):
      if file.endswith(".ini"):
          name_file = file.replace('.ini','')
          print("File Name: "+name_file)
          config = self.read_config(name_file)
          print("Key Pair: "+config['EC2INSTANCE']['pem_path'])
          print("User Pair: "+config['EC2INSTANCE']['user'])
          print("Instance Id Pair: "+config['EC2INSTANCE']['ec2_instance_id'])

      print (30 * '-')

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

  
    


