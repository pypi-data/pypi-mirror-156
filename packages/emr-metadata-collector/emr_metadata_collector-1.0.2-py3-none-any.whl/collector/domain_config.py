import boto3
import collector

class DomainConfig:

    def script_version(self):
        return collector.__version__