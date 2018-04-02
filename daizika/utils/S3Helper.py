import sys
import re
import boto3
import botocore

# Routines for S3 Processing
class S3Processor:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.s3_resource = boto3.resource('s3')
        self.bucket = self.s3_resource.Bucket(self.bucket_name)

    def get_s3_keys(self, filter_prefix):
        return self.bucket.objects.filter(Prefix=filter_prefix)

    #Checks if the key exists
    def does_exists(self, key):
        key_present = False
        objs = list(self.bucket.objects.filter(Prefix=key))
        if len(objs) > 0:
            key_present = True
        return key_present

    def delete_folder(self, file_prefix): 
        deleted = False
        try:
            counter = 1
            objects_to_delete = []
            for obj in self.get_s3_keys(file_prefix):
                objects_to_delete.append({'Key': obj.key})
                if counter > 900:
                    self.bucket.delete_objects(Delete={'Objects': objects_to_delete})
                    counter = 1
                    objects_to_delete = []
                counter += 1
            if len(objects_to_delete) > 0:
                self.bucket.delete_objects(Delete={'Objects': objects_to_delete})            
            self.bucket.delete_objects(Delete={'Objects': [{'Key': file_prefix}]})
            deleted = True
        except:
            print('Unexpected error: {}').format(sys.exc_info()[0])     
            raise
        return deleted
    
    def upload_to_s3(self, key, local_filename):
        attempt = 1
        keep_trying = 1
        upload_success = 0
        delay_timer = [1, 10, 30]
        while keep_trying == 1:
            try:
                self.s3_resource.Object(self.bucket_name, key).put(Body=open(local_filename, 'rb'))
                if self.does_exists(key):
                    keep_trying = 0
                    upload_success = 1
            except:
                print('Unexpected error: {}').format(sys.exc_info()[0])     
                raise
            if upload_success == 0 and attempt <= 3:
                time.sleep(delay_timer[attempt - 1])
                attempt += 1
            else:
                keep_trying = 0
        return upload_success
        