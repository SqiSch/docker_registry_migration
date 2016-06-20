#pip install docker-py

import json
import requests, json
import argparse
import sys
import os

from docker.client import Client
from docker.utils import kwargs_from_env

requests.packages.urllib3.disable_warnings()


parser = argparse.ArgumentParser(description='Migrate docker images from a v1 docker registry to a v2 registry')
parser.add_argument('source', help='source v1 registry')
parser.add_argument('dest', help='dest v2 registry')
parser.add_argument('-d', '--debug', action='store_true')


args = parser.parse_args()

docker_src_registry = ""
docker_dst_registry = ""
debug = args.debug

if args.source:
    api_images_url = "https://"+args.source+"/v1/search"
    docker_src_registry = args.source
else:
    sys.exit()

if args.dest:
    docker_dst_registry = args.dest
else:
    sys.exit()


from sys import platform as _platform
if _platform == "linux" or _platform == "linux2":
    kwargs = kwargs_from_env()
    client = Client(**kwargs)
elif _platform == "darwin":
    ## Create connection to local docker server
    kwargs = kwargs_from_env()
    kwargs['tls'].assert_hostname = False
    client = Client(**kwargs)
elif _platform == "win32":
    # Windows...
    print "Warn: Not tested"




# Get all images from source
r = requests.get( api_images_url )
if debug: print r
images = r.json()['results']


def pull_image_to_local(image_tag, tag):
    print 'pulling :', image_tag
    for line in client.pull(image_tag, tag, stream=True):
        if debug: print(json.dumps(json.loads(line), indent=4))
    return

def tag_image(image, repository, tag):
    print 'tag : '+image+' + repository:'+repository+":"+tag
    client.tag(image+":"+tag, repository, tag, force=True)
    return

def push_image(image_tag):
    print 'push : '+image_tag
    for line in client.push(image_tag, stream=True):
        if debug: print(json.dumps(json.loads(line), indent=4))
    return

def remove_image_local(pull_src, push_dest, tag):
    print 'remove  : src: '+pull_src+' + dst: '+push_dest
    client.remove_image(pull_src+":"+tag)
    client.remove_image(push_dest+":"+tag)
    return

def pull_tag_push_remove(pull_src, push_dest, tag ):
    pull_image_to_local(pull_src, tag)
    tag_image(pull_src, push_dest, tag)
    push_image(push_dest+":"+tag)
    remove_image_local(pull_src, push_dest, tag)
    return

for image in images:       # Loop through images
   print 'pulling all tags from image :', image['name']

   # Get all tags for a image
   api_image_tags_url = "https://"+docker_src_registry+"/v1/repositories/"+image['name']+"/tags"
   r = requests.get( api_image_tags_url )
   tags = r.json()

   for tag, id in tags.iteritems(): # Loop through tags for a image
     # check if tag exists in new docker registry.
      print 'pulling tag from image :', tag
      new_api_image_tags_url = "https://"+docker_dst_registry+"/v2/"+image['name']+"/tags/list"
      print new_api_image_tags_url
      r = requests.get( new_api_image_tags_url, verify=False )
      new_tags = r.json()


      pull_image_src = docker_src_registry+"/"+image['name']
      tag_image_dst = docker_dst_registry+"/"+image['name']

      try:
          if tag == 'latest':
               print "pull latest tag and push it"
               pull_tag_push_remove(pull_image_src, tag_image_dst, tag)
          else:
              if tag in new_tags['tags']:
                  print "tag is already pushed."
              else:
                 pull_tag_push_remove(pull_image_src, tag_image_dst, tag)
                 print "tag not inside. Pulling and push it"
      except KeyError, e:
         print 'Image is not present. Pull and Push it. '
         pull_tag_push_remove(pull_image_src, tag_image_dst, tag)
