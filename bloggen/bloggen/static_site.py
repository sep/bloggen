from google.cloud import storage
import os
import markdown
import time
import sys
import bloggen.generate as generate

class Site:
    def __init__(self, user_config):
        self.user_config = user_config
        self.client = storage.Client()
        self.bucket_name = self.user_config.active_config['data']['buckets'][0]
        self.host_url = 'https://storage.cloud.google.com/'
        self.bucket = None
        self.retrieve_bucket(self.bucket_name)
        #blob = self.bucket.blob('notes/index.html')
        #blob.upload_from_filename('notes/index.html')

    def add(self, path_to_md):
        with open(path_to_md) as f:
            md_input = f.read()
        filename = os.path.basename(path_to_md)[:-3]
        outfile = f'notes/{filename}.html'
        html = markdown.markdown(md_input)
        with open(outfile, 'w') as f:
            f.write(html)
        blob = self.bucket.blob(outfile)
        blob.upload_from_filename(outfile)

    def publish(self, path_to_static_site:str=generate.get_static_site_dir()):
        # need to prepare for hosting site:
            # replace all local hrefs with refs to files on cloud.
            # Will follow this pattern: https://storage.cloud.google.com/first-bloggen-bucket/static-site/notes/test%20copy%202.html
        notes_root = f"{self.host_url}{self.bucket_name}/static-site/notes/"
        generate.prep_for_hosting(notes_root)

        # learn which bucket to use
        target_bucket_name = self.user_config.active_config['data']['buckets'][0] if len(self.user_config.active_config['data']['buckets']) < 2 else input(f"Which bucket? {self.user_config.active_config['data']['buckets']}")
        # learn if bucket exists
        target_bucket = self.retrieve_bucket(target_bucket_name)

        if target_bucket:
            print('uploading bucket')
            self.upload_site(path_to_static_site)
            bucket_url = f"{self.host_url}{target_bucket_name}/static-site/index.html"
            print(f'Your notes are available as html at {bucket_url}')
        else:
            print("Bucket not insantiated",file=sys.stderr)

    def generate(self, path_to_md_dir=os.getcwd()):
        generate.html_files(path_to_md_dir)
        generate.index()
        print(f'See your local site at {os.path.join(generate.get_static_site_dir(),"index.html")}')

    def get_bucket(self, name):
        return self.client.get_bucket(name)

    def make_bucket(self, name):
        self.bucket: storage.Bucket = self.client.create_bucket(name)

    def set_privacy(self, public: bool):
        if public:
            self.bucket.make_public
        else:
            self.bucket.make_private

    def upload_site(self, path_to_dir:str):
        root = os.path.basename(path_to_dir)
        for path, _, files in os.walk(path_to_dir):
            for name in files:
                print(f'uploading file {name}')
                root_index = path_to_dir.find(root)
                print(root_index)
                blob_path = os.path.join(path, name).replace('\\','/')[root_index:]
                print('blob path: '+blob_path)
                blob = self.bucket.blob(blob_path)
                local_path = os.path.join(path, name)
                blob.upload_from_filename(local_path)

    def upload_files(self, path_to_dir) -> str:
        print(path_to_dir)
        for path, _, files in os.walk(path_to_dir):
            for name in files:
                print(f'uploading {name}')
                path_local = os.path.join(path, name)
                blob_path = path_local.replace('\\','/')
                blob = self.bucket.blob(blob_path)
                blob.upload_from_filename(path_local)

    def retrieve_bucket(self, bucket_name):
        try:
            return self.get_bucket(bucket_name)
        except:
            bucket = self.make_bucket(bucket_name)
            print(f'Creating a new bucket named {bucket_name}')
            time.sleep(4)
            return bucket