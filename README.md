# ec2ssh
Ec2ssh allows you to easily manage all its ssh connections to instances hosted on AWS.

# Features
* Create a direct Conncetion to EC2 Instances
* Create a tunneling connection to EC2 Instance passing by an a BastionHost
* Create a connection to an ASG passing by an a BastionHost
* Using differente AWS cli profiles
* Specify Region connection
* Add/Remove connection easly

# New Feature
* provide multiterm whit TMUX, now you can connect whit all your ASG instaces whit 1 command

## Requirement
There are a small list of requirement:
* Python 3
* Pip
* AWS cli configured 
* tmux


## Usage
Ec2ssh use a series of infomation to connect with the Ec2 Instance. To configure the connection, depending on the type you want to use, you must provide the Instance ID, its region the PEM key and the user to connect to.

For Example for connect to ASG you need to provide:
* EC2 KeyPair Pem File
* EC2 UserName for ssh connection
* ASG Name
* Bastion Pem
* Bastion User
* Bastion Instance Id


Below the available commands and parameters

commands:

* ec2ssh add 'connection_name'        => to add a connection name
* ec2ssh connect 'connection_name'    => connect to ec2
* ec2ssh ls                           => to list avaible connections
* ec2ssh rm 'connection_name'         => remove a connection


Usage: ec2ssh [command] [name] [options] arg1 arg2
AWS configuration is REQUIRED
Options:
* -h, --help            show this help message and exit
* -c, --commands        list all Commands
* -p PROFILE_NAME, --profile=PROFILE_NAME use Specific Profile



Feel free to contribute or comment my code!