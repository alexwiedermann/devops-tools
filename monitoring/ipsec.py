#!/usr/bin/env python

# Import JSON module
import json
import socket

# Import for requests http
from requests import get

# Import for file check
import os.path

# Import AWS API
import boto3

# Import Error Handler
from botocore.exceptions import ClientError

# Import argparse
import argparse
# Variables
oldip_path = "/tmp/oldip.txt"
iplist_path = "/tmp/iplist.txt"
def revoke_authorize(oldip,ip,region):
    ec2 = boto3.client("ec2",region_name=region)
    all_sg = ec2.describe_security_groups()
    oldip = oldip.replace('\n','')
    for group in all_sg['SecurityGroups']:
        try:
            if group['GroupName'] == "WHITELISTEDGROUP":
                print "Regra nao adicionada no grupo WHITELISTEDGROUP"
            else:
                ec2.revoke_security_group_ingress(GroupId=group['GroupId'],IpProtocol="tcp",CidrIp=oldip+"/32",FromPort=0,ToPort=65535)
                print "Regra removida para o ip " + oldip +" no grupo: %s" % group['GroupName']
                ec2.authorize_security_group_ingress(GroupId=group['GroupId'],IpProtocol="tcp",CidrIp=ip+"/32",FromPort=0,ToPort=65535)
                print "Regra adicionada no grupo: %s" % group['GroupName']
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidPermission.Duplicate':
                print "IP "+ ip + "/32 Ja Cadastrado"
            elif e.response['Error']['Code'] == 'InvalidPermission.NotFound':
                    print "IP nao existe neste SG"
            else:
                print "Erro nao esperado: %s" % e

def authorize(ip,region):
    ec2 = boto3.client("ec2",region_name=region)
    all_sg = ec2.describe_security_groups()
    for group in all_sg['SecurityGroups']:
        try:
            if group['GroupName'] == "WHITELISTEDGROUP":
                print "Regra nao adicionada no grupo WHITELISTEDGROUP"
            else:
                ec2.authorize_security_group_ingress(GroupId=group['GroupId'],IpProtocol="tcp",CidrIp=ip+"/32",FromPort=0,ToPort=65535)
                print "Regra adicionada no grupo: %s" % group['GroupName']
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidPermission.Duplicate':
                print "IP "+ ip + "/32 Ja Cadastrado"
            elif e.response['Error']['Code'] == 'InvalidPermission.NotFound':
                    print "IP nao existe neste SG"
            else:
                print "Erro nao esperado: %s" % e

def write_oldip(ip):
    file = open(oldip_path,"w")
    file.write(ip)
    file.close()

iplist_path = "/tmp/iplist.txt"
ip = get('https://api.ipify.org').text
if ip == "0.0.0.0": # Whitelist IP
    print "Whitelist"
    exit(0)
if os.path.exists(oldip_path):
    file = open(oldip_path,"r") 
    oldip = file.read()
    file.close()
    if ip == oldip:
        print ("O IP nao mudou")
        exit(0)
    else:
        file = open(oldip_path,"w")
        file.write(ip)
        file.close()
        try:
            socket.inet_pton(socket.AF_INET, oldip)
        except socket.error:  # not a valid address
            print "First execution"
            file = open(oldip_path,"w")
            file.write(ip)
            file.close()
            region="sa-east-1"
            authorize(ip,region)
            region="us-east-1"
            authorize(ip,region)
            write_oldip(ip)
            exit(0)
        region="sa-east-1"
        revoke_authorize(oldip,ip,region)
        region="us-east-1"
        revoke_authorize(oldip,ip,region)
        write_oldip(ip)
        exit(0)
else:
    print "First execution"
    file = open(oldip_path,"w")
    file.write(ip)
    file.close()
    region="sa-east-1"
    authorize(ip,region)
    region="us-east-1"
    authorize(ip,region)
    write_oldip(ip)
