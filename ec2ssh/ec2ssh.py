import subprocess
import sys
import boto3
import configparser
import os

#class ec2ssh:


#conn = ec2ssh()

#print(sys.argv[1])
#conn.main(sys.argv[1])

def read_config(host):
  config = configparser.ConfigParser()
  config.sections()
  config.read(host+'.ini')
  return(config);

def addConfig(args):
  config = configparser.ConfigParser()

  printMenu()

  is_valid=0

  valid_choise=0
  usr_input = ''
  while usr_input not in ['1', '2']:
    if valid_choise :
      print("Not Valid Choise")
    valid_choise=1
    usr_input = input("Input: ")

  if usr_input == "1":
    config['EC2INSTANCE'] = {}
    config['EC2INSTANCE']['pem_path'] = input('Enter a pem file path: ')
    config['EC2INSTANCE']['user'] = input('Enter a user: ')
    config['EC2INSTANCE']['ec2_instance_id'] = input('Enter a Instance ID: ')
  elif usr_input == "1":
    config['EC2INSTANCE'] = {}
    config['EC2INSTANCE']['pem_path'] = input('Enter a pem file path: ')
    config['EC2INSTANCE']['user'] = input('Enter a user: ')
    config['EC2INSTANCE']['ec2_instance_id'] = input('Enter a Instance ID: ')
    config['BASTIONHOST'] = {}
    config['BASTIONHOST']['b_pem_path'] = input('Enter a Bastion pem file path: ')
    config['BASTIONHOST']['b_user'] = input('Enter a Bastion user: ')
    config['BASTIONHOST']['b_ec2_instance_id'] = input('Enter a Bastion Instance ID: ')

  with open(args[2]+'.ini', 'w') as configfile:
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



def main():
  args = sys.argv
  switcher = {
    "add":addConfig,
    "connect": ec2ssh
  }
  return switcher[args[1]](args)