# cloud_formation_blog
This repository contains code on how to deploy CloudFormation scripts using boto3.

Link to blog-

https://medium.com/aws-blogs/configuring-aws-data-pipeline-using-cloudformation-efea831e9bed

## Pre Requisites
To run the code from your local system you must have the following
1. python 3.7
2. boto 3
```bash
pip install boto3
```
3. AWS tokens configured.

## How to run the program
1. Clone the git repository.
```bash
git clone https://github.com/surya-de/cloud_formation_blog.git
```
2. Add your lambda functions in the following folder.
```
cd surya-de/cloud_formation_blog
```
3. Run the python file. Make sure to add the stack name at the end.
```bash
python deploy_scripts.py stack_name
```
