import subprocess
import boto3
import sys
import configparser
from codecs import open
from os.path import expanduser
import os
import glob


hosts_folder = expanduser("~")

directory_to_save = hosts_folder+'/.ec2ssh/hosts/'

def read_config(host):
  if os.path.isfile(directory_to_save+host+'.ini'):
    config = configparser.ConfigParser()
    config.sections()
    config.read(directory_to_save+host+'.ini')
    return(config);
  else:
    sys.exit("File Host doesn't exist")


def addConfig(args):

  config = configparser.ConfigParser()
  printMenu()
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
  elif usr_input == "1":
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

  with open(directory_to_save+args[2]+'.ini', 'w') as configfile:
    config.write(configfile)

  print("File Config "+args[2]+" created")

def printMenu():
  print (30 * '-')
  print ("   M A I N - M E N U")
  print (30 * '-')
  print ("1. Direct Connect")
  print ("2. Pass from Bastion Host")
  print (30 * '-')

def ec2ssh(args):
  config = read_config(args[2])
  target = {'key': config['EC2INSTANCE']['pem_path'], 'user': config['EC2INSTANCE']['user'], 'host': config['EC2INSTANCE']['ec2_instance_id']}
  target_ec2 = boto3.client('ec2')
  target_response = target_ec2.describe_instances(InstanceIds=[target['host']])


  if config.has_section('BASTIONHOST'):
    bastion = {'key': config['BASTIONHOST']['b_pem_path'], 'user': config['BASTIONHOST']['b_user'], 'host': config['BASTIONHOST']['b_ec2_instance_id']}
    bastion_ec2 = boto3.client('ec2')
    bastion_response = bastion_ec2.describe_instances(InstanceIds=[bastion['host']])
    bastion_ip = bastion_response['Reservations'][0]['Instances'][0]['PublicIpAddress']

    target_ip = target_response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['PrivateIpAddress']

    subprocess.call("ssh-add {} {}".format(bastion['key'], target['key']), shell=True)
    subprocess.call("ssh -t -A {}@{} ssh {}@{}".format(bastion['user'], bastion_ip, target['user'], target_ip), shell=True)

  else:
    target_ip = target_response['Reservations'][0]['Instances'][0]['PublicIpAddress']
    subprocess.call("ssh-add {}".format(target['key']), shell=True)
    subprocess.call("ssh {}@{}".format(target['user'], target_ip), shell=True)

def list_avaible_connection(args):
  print (30 * '-')
  for file in os.listdir(directory_to_save):
    if file.endswith(".ini"):
        name_file = file.replace('.ini','')
        print("File Name: "+name_file)
        config = read_config(name_file)
        print("Key Pair: "+config['EC2INSTANCE']['pem_path'])
        print("User Pair: "+config['EC2INSTANCE']['user'])
        print("Instance Id Pair: "+config['EC2INSTANCE']['ec2_instance_id'])

    print (30 * '-')


def main():
  if not os.path.exists(directory_to_save):
    os.makedirs(directory_to_save)
  args = sys.argv
  switcher = {
    "add":addConfig,
    "connect": ec2ssh,
    "ls": list_avaible_connection
  }
  return switcher[args[1]](args)
