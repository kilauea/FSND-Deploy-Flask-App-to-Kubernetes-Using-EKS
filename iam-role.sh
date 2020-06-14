#!/bin/bash

function pause(){
 read -s -n 1 -p "Press any key to continue . . ."
 echo ""
}

function create_eks_cluster(){
  eksctl create cluster --name simple-jwt-api
}

function delete_eks_cluster(){
  eksctl delete cluster --name simple-jwt-api
}

function creatre_iam_role(){
  ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

  TRUST="{ \"Version\": \"2012-10-17\", \"Statement\": [ { \"Effect\": \"Allow\", \"Principal\": { \"AWS\": \"arn:aws:iam::${ACCOUNT_ID}:root\" }, \"Action\": \"sts:AssumeRole\" } ] }"

  aws iam create-role --role-name UdacityFlaskDeployCBKubectlRole --assume-role-policy-document "$TRUST" --output text --query 'Role.Arn'

  echo '{ "Version": "2012-10-17", "Statement": [ { "Effect": "Allow", "Action": [ "eks:Describe*", "ssm:GetParameters" ], "Resource": "*" } ] }' > /tmp/iam-role-policy

  aws iam put-role-policy --role-name UdacityFlaskDeployCBKubectlRole --policy-name eks-describe --policy-document file:///tmp/iam-role-policy

  kubectl get -n kube-system configmap/aws-auth -o yaml > /tmp/aws-auth-patch.yml

  cat /tmp/aws-auth-patch.yml

  echo "Make sure your ACCOUNT_ID $ACCOUNT_ID is set in /tmp/aws-auth-patch.yml"

  read -p "Is your ACCOUNT_ID OK (y/n)? " answer
  case ${answer:0:1} in
    y|Y )
      kubectl patch configmap/aws-auth -n kube-system --patch "$(cat /tmp/aws-auth-patch.yml)"
      ;;
    * )
      exit
    ;;
  esac
}

function set_secret(){
  aws ssm put-parameter --overwrite --name JWT_SECRET --value "1Ie9dk309dh3rf8^3Sl$" --type SecureString
}

read -p "Create EKS Cluster (y/n)? " answer
case ${answer:0:1} in
  y|Y )
    create_eks_cluster
    ;;
  * )
    echo No
  ;;
esac

read -p "Create IAM Role (y/n)? " answer
case ${answer:0:1} in
  y|Y )
    creatre_iam_role
    ;;
  * )
    echo No
  ;;
esac

read -p "Set Secret (y/n)? " answer
case ${answer:0:1} in
  y|Y )
    set_secret
    ;;
  * )
    echo No
  ;;
esac

read -p "Delete EKS Cluster (y/n)? " answer
case ${answer:0:1} in
  y|Y )
    delete_eks_cluster
    ;;
  * )
    echo No
  ;;
esac
