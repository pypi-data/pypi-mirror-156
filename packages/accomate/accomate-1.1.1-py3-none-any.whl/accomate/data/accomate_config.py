import os
import pickle
from accomate.aws.route53 import get_hosted_zone_id
from accomate.utils.network import get_machine_public_ip

from accomate.utils.yaml_file import read_yaml_file


class AccomateConfig(object):

    def __init__(self, user: str, use_cache: bool = False):

        self.__name = 'accomate'
        self.__version = '1.0.6'

        if user is not None:
            self.__config = None
            self.__base_path = f"/home/{user}/accomate"
            self.__config_path = f"{self.__base_path}/config.yaml"
            self.__cache_config_path = f"{self.__base_path}/.accoladez"
            self.__base_domain = 'itdaycloud.com'
            self.__log_path = f"{self.__base_path}/logs"
            self.__base_store_path = f"{self.__base_path}/stores"
            self.__store_service_images = {
                "2.0.0": "042826358439.dkr.ecr.us-east-1.amazonaws.com/accoladez-store:2.0.0",
                "2.0.1": "042826358439.dkr.ecr.us-east-1.amazonaws.com/accoladez-store:2.0.1",
                "2.0.2": "042826358439.dkr.ecr.us-east-1.amazonaws.com/accoladez-store:2.0.2",
                "latest": "042826358439.dkr.ecr.us-east-1.amazonaws.com/accoladez-store:latest",
            }
            self.__auth_service_images = {
                "1.0.0": "042826358439.dkr.ecr.us-east-1.amazonaws.com/accoladez-auth:1.0.0",
                "2.0.0": "042826358439.dkr.ecr.us-east-1.amazonaws.com/accoladez-auth:2.0.0",
                "2.0.1": "042826358439.dkr.ecr.us-east-1.amazonaws.com/accoladez-auth:2.0.1",
                "2.0.2": "042826358439.dkr.ecr.us-east-1.amazonaws.com/accoladez-auth:2.0.2",
                "latest": "042826358439.dkr.ecr.us-east-1.amazonaws.com/accoladez-auth:latest",
            }
            self.__base_nginx_path = f"{self.__base_path}/nginx/conf"
            self.__machine_ip_address = get_machine_public_ip().strip()
            self.__hosted_zone_id = get_hosted_zone_id(self.__base_domain)
        if use_cache:
            if os.path.exists(self.__cache_config_path):
                with open(self.__cache_config_path, 'rb') as f:
                    self = pickle.load(f)
                    print(f"Using cached config", end='\n')
            else:
                print("No cache found!", end="\n")

    def load_config(self):
        # load the config from the yaml file
        self.__config = read_yaml_file(self.__config_path)
        if self.__config is None:
            print("Config file not found")
            exit(1)
        else:
            print("Config file loaded")
            self.__base_path = self.__config['base_path']
            self.__config_path = f"{self.__base_path}/config.yaml"
            self.__cache_config_path = f"{self.__base_path}/.accoladez"
            self.__log_path = f"{self.__base_path}/logs"
            self.__base_store_path = f"{self.__base_path}/stores"
            self.__base_nginx_path = f"{self.__base_path}/nginx/conf"

            self.__store_service_images = self.__config['store_service_images']
            self.__auth_service_images = self.__config['auth_service_images']
            self.__base_domain = self.__config['base_domain']
            self.__machine_ip_address = get_machine_public_ip().strip()
            self.__hosted_zone_id = get_hosted_zone_id(self.__base_domain)
            self.cache()

    def get_config_path(self):
        return self.__config_path

    def get_base_path(self):
        return self.__base_path

    def get_stores_path(self):
        return self.__base_store_path

    def get_domain(self):
        return self.__base_domain

    def get_store_service_images(self):
        return self.__store_service_images

    def get_auth_service_images(self):
        return self.__auth_service_images

    def get_zone_id(self):
        return self.__hosted_zone_id

    def get_public_ip(self):
        return self.__machine_ip_address

    def get_nginx_path(self):
        return self.__base_nginx_path

    def cache(self):
        # cache this config in the pickle file
        with open(self.__cache_config_path, 'wb') as f:
            pickle.dump(self, f)
        
