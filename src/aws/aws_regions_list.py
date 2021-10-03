import boto3

# TODO:
#   - move this into a class-static initializer
#
ssm = boto3.client('ssm')


# Before this script can be executed, the current authenticated AWS user
# needs to have at minimum the following permissions (permissions policy):
#
#   AmazonSSMReadOnlyAccess
#
# either attached directly to the IAM user or through a group.
#
class Regions:
    @classmethod
    def get_regions(cls):
        short_codes = cls._get_region_short_codes()

        regions = [{
            'name': cls._get_region_long_name(sc),
            'code': sc
        } for sc in short_codes]

        regions_sorted = sorted(
            regions,
            key=lambda k: k['name']
        )

        return regions_sorted

    @classmethod
    def _get_region_long_name(cls, short_code):
        param_name = (
            '/aws/service/global-infrastructure/regions/'
            f'{short_code}/longName'
        )
        response = ssm.get_parameters(
            Names=[param_name]
        )
        return response['Parameters'][0]['Value']

    @classmethod
    def _get_region_short_codes(cls):
        output = set()
        for page in ssm.get_paginator('get_parameters_by_path').paginate(
            Path='/aws/service/global-infrastructure/regions'
        ):
            output.update(p['Value'] for p in page['Parameters'])

        return output



if __name__ == "__main__":
    for region in Regions.get_regions():
        print(region)
