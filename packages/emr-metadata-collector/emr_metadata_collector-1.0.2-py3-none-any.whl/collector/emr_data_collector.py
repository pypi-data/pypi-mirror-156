import os
import datetime
from zipfile import ZipFile
from yaml import load
import requests
import boto3
from requests_aws4auth import AWS4Auth
from collector.domain_config import DomainConfig
import collector



def list_clusters(region):
    emr_client = boto3.client('emr', region_name=region)
    clusters = emr_client.list_clusters(ClusterStates=[
        'STARTING','BOOTSTRAPPING','RUNNING','WAITING'
    ],)
    print("Cluster List:")
    for cluster in clusters["Clusters"]:
        print("Name:" + cluster["Name"] + ". ID:" + cluster["Id"])


def collect_data(region,cluster_id,output_dir):
    emr_client = boto3.client('emr', region_name=region)
    response = emr_client.describe_cluster(
        ClusterId=cluster_id
    )
    with open(output_dir + "/cluster_" + cluster_id + "_describe.json", "w") as dest:
        dest.write(str(response))

    status = response["Cluster"]["Status"]
    ec2_key_name = response["Cluster"]["Ec2InstanceAttributes"]["Ec2KeyName"]
    applications = response["Cluster"]["Applications"]
    instance_collection_type = response["Cluster"]["InstanceCollectionType"]

    if instance_collection_type == "INSTANCE_FLEET":
        list_instance_fleets(emr_client,cluster_id,output_dir)
    elif instance_collection_type == "INSTANCE_GROUP":
        list_instance_groups(emr_client,cluster_id,output_dir)


def list_instance_fleets(client,cluster_id,output_dir):
    instance_fleets_response = client.list_instance_fleets(
        ClusterId=cluster_id
    )
    with open(output_dir + "/cluster_"+cluster_id+"_instancefleets.json", "w") as dest:
        dest.write(instance_fleets_response)

def list_instance_groups(client,cluster_id,output_dir):
    instance_groups_response = client.list_instance_groups(
        ClusterId=cluster_id
    )
    with open(output_dir + "/cluster_"+cluster_id+"_instancegroups.json", "w") as dest:
        dest.write(str(instance_groups_response))

    for instance_group in instance_groups_response["InstanceGroups"]:
        instance_group_id = instance_group["Id"]
        instance_group_name = instance_group["Name"]
        instance_group_market = instance_group["Market"]
        instance_group_type = instance_group["InstanceGroupType"]
        instance_group_instance_type = instance_group["InstanceType"]
        #instance_group_ebs_optimized = instance_group["EbsOptimized"]
        # print("instance group id: {}, instance_group_name:{}, instance_group_market:{}, instance_group_type:{}, instance_group_instance_type:{}".format(
        #       instance_group_id,instance_group_name,instance_group_market,instance_group_type,instance_group_instance_type))
        collect_data_for_instance_group(client, cluster_id, instance_group_id,instance_group_type,output_dir)


def collect_data_for_instance_group(client, cluster_id, instance_group_id,instance_group_type,output_dir):
    instance_response = client.list_instances(
        ClusterId=cluster_id,
        InstanceGroupId=instance_group_id
    )
    with open(output_dir + "/cluster_"+cluster_id+ "_"+instance_group_type + "_" +instance_group_id +"_instancegroup.json", "w") as dest:
        dest.write(str(instance_response))
    for instance in instance_response["Instances"]:
        instance_id = instance["Id"]
        ec2_instance_id = instance["Ec2InstanceId"]
        public_dns_name = instance["PublicDnsName"]
        private_dns_name = instance["PrivateDnsName"]
        public_ip_address = instance["PublicIpAddress"]
        ec2_status = instance["Status"]["State"]
        ebs_volumes = instance["EbsVolumes"]
        # print(
        #     "instance id:{},ec2_instance_id:{},public_dns_name:{},public_ip_address:{},ec2_status:{},ebs_volumes:{}".format(
        #         instance_id, ec2_instance_id, public_dns_name, public_ip_address, ec2_status, str(ebs_volumes)))
        if ec2_status == "RUNNING":
            if instance_group_type == "MASTER":
                collect_data_for_master_instance_group(client, cluster_id, instance_group_id,instance_group_type,
                                                       instance_id,public_dns_name,private_dns_name,output_dir)
            elif instance_group_type == "CORE":
                collect_data_for_core_instance_group(client, cluster_id, instance_group_id,instance_group_type,
                                                     instance_id,public_dns_name,private_dns_name,output_dir)
            elif instance_group_type == "TASK":
                collect_data_for_task_instance_group(client, cluster_id, instance_group_id,instance_group_type,
                                                     instance_id,public_dns_name,private_dns_name,output_dir)

def collect_data_for_master_instance_group(client, cluster_id, instance_group_id,instance_group_type,instance_id,
                                           public_dns_name,private_dns_name,output_dir):
    rest_host_address= "http://" + public_dns_name +":16010"
    run_actions(rest_host_address,cluster_id, instance_group_id,instance_group_type,instance_id,public_dns_name,private_dns_name,output_dir)

def collect_data_for_core_instance_group(client, cluster_id, instance_group_id,instance_group_type,instance_id,
                                         public_dns_name,private_dns_name,output_dir):
    rest_host_address = "http://" + public_dns_name + ":16030"
    run_actions(rest_host_address, cluster_id, instance_group_id, instance_group_type, instance_id, public_dns_name,private_dns_name,output_dir)

def collect_data_for_task_instance_group(client, cluster_id, instance_group_id,instance_group_type,instance_id,
                                         public_dns_name,private_dns_name,output_dir):
    rest_host_address = "http://" + public_dns_name + ":16030"
    run_actions(rest_host_address, cluster_id, instance_group_id, instance_group_type, instance_id, public_dns_name,private_dns_name,
                output_dir)

def run_actions(rest_host_address,cluster_id, instance_group_id,instance_group_type,instance_id,public_dns_name,private_dns_name,output_dir):
    try:
        from yaml import CLoader as Loader, CDumper as Dumper
    except ImportError:
        from yaml import Loader, Dumper
    config_file = os.path.join(collector.__path__[0],"action_config.yml")
    with open(config_file) as f:
        config = load(f,Loader=Loader)
    for action in config:
        print("action:" + action + ":" + config[action]["cmd_type"] + ":" + config[action]["cmd"] + "->" + config[action]["file"])
        if(config[action]["cmd_type"] == "rest"):
            if config[action]["cmd"] == "/logs" :
                URL = rest_host_address + config[action]["cmd"] + "/"
                file_name=""
                if instance_group_type == "MASTER":
                    file_name = "hbase-hbase-master-"
                elif instance_group_type == "CORE":
                    file_name = "hbase-hbase-regionserver-"
                elif instance_group_type == "TASK":
                    file_name = "hbase-hbase-regionserver-"
                host_name=private_dns_name.split(".")[0]
                now = datetime.datetime.now()
                one_hour_before = now - datetime.timedelta(hours=1)
                two_hour_before = now - datetime.timedelta(hours=2)
                year = '{:02d}'.format(one_hour_before.year)
                month = '{:02d}'.format(one_hour_before.month)
                day = '{:02d}'.format(one_hour_before.day)
                hour = '{:02d}'.format(one_hour_before.hour)
                two_hour = '{:02d}'.format(two_hour_before.hour)
                hour_day_month_year = '{}-{}-{}-{}'.format(year, month, day,hour)
                two_hour_day_month_year = '{}-{}-{}-{}'.format(year, month, day, two_hour)
                current_file_name=file_name + host_name + ".log"
                file_name_1 = file_name + host_name + ".log." + hour_day_month_year
                file_name_2 = file_name + host_name + ".log." + two_hour_day_month_year
                dowload_file(URL, current_file_name, output_dir)
                dowload_file(URL, file_name_1, output_dir)
                dowload_file(URL, file_name_2, output_dir)
            else:
                URL = rest_host_address + config[action]["cmd"]
                response = requests.get(URL)
                status_code = response.status_code
                if status_code == 200:
                    with open(output_dir + "/cluster_"+cluster_id+ "_"+instance_group_type + "_" +instance_group_id + "_" +instance_id + "_" + config[action]["file"], "w") as dest:
                        dest.write(response.text)
                else:
                    print("ERROR when collecting metadata: " + response.text)
                    with open(output_dir + "/cluster_"+cluster_id+ "_"+instance_group_type + "_" +instance_group_id + "_" +instance_id + "_" + config[action]["file"], "w") as dest:
                        dest.write(response.text)
                    #exit(1)
        elif(config[action]["cmd_type"] == "method"):
            obj = DomainConfig()
            func = getattr(obj, config[action]["cmd"],"invalid config for method call")
            #func = getattr(collector.elasticsearch_data_collector, config[action]["cmd"], "invalid config for method call")
            if callable(func):
                if (config[action]["need_params"]):
                    out = func("region", "domain")
                else:
                    out = func()
            with open(output_dir + "/" + config[action]["file"], "w") as dest:
                dest.write(str(out))
        else:
            print("invalid cmd type for " + action)


def dowload_file(URL, file_name, output_dir):
    URL = URL + file_name
    response = requests.get(URL)
    status_code = response.status_code
    if status_code == 200:
        with open(
                output_dir + "/logs/" + file_name, "w") as dest:
            dest.write(response.text)


def archive_files(output_dir):
    compressed_files = output_dir + ".zip"
    parent_folder = os.path.dirname(output_dir)
    with ZipFile(compressed_files, 'w') as zipObj:
        for folderName, subfolders, filenames in os.walk(output_dir):
            for filename in subfolders:
                absolute_path = os.path.join(folderName, filename)
                relative_path = absolute_path.replace(parent_folder + '\\','')
                print("Adding '%s' to archive." % absolute_path)
                zipObj.write(absolute_path, relative_path)
            for filename in filenames:
                absolute_path = os.path.join(folderName, filename)
                relative_path = absolute_path.replace(parent_folder + '\\','')
                print("Adding '%s' to archive." % absolute_path)
                zipObj.write(absolute_path, relative_path)
    print("Completed EMR Metadata collection. Please send " + compressed_files + " to AWS team.")
