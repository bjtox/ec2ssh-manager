# ec2ssh
Python script to facilitate SSH access to AWS EC2 instances with dynamic IPs or behind bastion hosts

ec2ssh uses subprocess.call to connect via SSH to EC2 instances on Amazon Web Services and Boto 3 to get the curret public static IP address of the instance.
This way you don't have to allocate an Elastic IP Address to conveniently connect via SSH to the instance, or repeatedly check it's current static IP address.

This script is in extremely early stage, but it works (I'm currently using it). It's mostly a way for me to start using and learning Python.

To get the static IP address of the instance and connect you have to provide the program with an identity file with the following information:  
* Path to the key pair file for the host
* User
* EC2 Instance ID

Also, Boto 3 must be able to call the AWS EC2 API, which requires AWS credentials. Ideally, you should install the AWS CLI (sudo pip install awscli) and configure it with your credentials (aws configure).

ec2ssh also supports SSH connections via a bastion host, in which case the identity file must also contain the path to the bastion host key pair, the user for the bastion host and the EC2 Instance ID of the bastion host.

What it's curretly lacking:  
* A cli command to create a new identity file (which will ask you if you are using a bastion host or not, followed by the required data)
* It does not check for any kind of error or exception
* It's not a Python module yet, it's just a .py script file; ideally it will install itself via pip in the Python modules folder (the identity files will be saved there too)

ec2ssh add <connection_name>        => to add a connection name
ec2ssh connect <connection_name>    => connect to ec2
ec2ssh ls                           => to list avaible connections
ec2ssh rm <connection_name>         => remove a connection

Feel free to contribute or comment my code!