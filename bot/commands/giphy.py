# import boto3
# import os
# import requests
# import time
#
# from botocore.client import Config
# from botocore.vendored.requests.exceptions import ConnectionError
# from io import BytesIO
#
# from bot.command_map import command_map
# from bot.config import config
#
# # Python doesn't know where to load the ImageMagick library in the context of apollo/brazil
# # Need to figure out the correct path
# #from wand.image import Image
# #from wand.api import library
#
#
# gif_url = 'https://media3.giphy.com/media/EOHiotyECxaPC/giphy.gif'  # Because it's funny
# aws_credentials = config.get_aws_credentials(decode=True)  # Curse this decoding material set in particular!
# session = boto3.Session(aws_access_key_id=aws_credentials[0], aws_secret_access_key=aws_credentials[1], region_name='us-east-1')
# s3 = session.client('s3', config=Config(signature_version='s3v4', connect_timeout=5))
# bucket_name = config.gif_bucket
#
#
# @command_map.register_command()
# def gif(query=[], user=None):
#     '''Get a gif'''
#     global gif_url
#     payload = {'api_key': config.giphy_api_key, 's': '+'.join(query)}
#     req = requests.get("http://api.giphy.com/v1/gifs/translate", payload)
#
#     try:
#         gif_url = req.json()['data']['images']['original']['url'].replace('http://', 'https://')
#         return gif_url
#     except Exception:
#         return 'https://i.imgur.com/7KLw9Gk.png'
#
#
# @command_map.register_command()
# def reverse(query=[], user=None):
#     '''Reverses the last gif returned from giphy or the given gif url'''
#     if query:
#         url = query[0]
#     else:
#         url = gif_url
#
#     # Get GIF
#     try:
#         req = requests.get(url)
#         with Image(blob=req.content) as img:
#             img.wand = library.MagickCoalesceImages(img.wand)
#             # Need to save for changes to take place since this only modifies the pointer and not the Sequence of images
#             temp = BytesIO()
#             img.save(file=temp)
#
#     except Exception as e:
#         return "Are you sure that's a jif?"
#
#     b = BytesIO()
#     with Image(blob=temp.getvalue()) as img:
#         with Image() as output:
#             # Have to clone the first frame as it contains looping information
#             # somehow library.MagickSetOption(seq[0].wand, 'loop', '0') doesn't work
#             first = img.sequence[0].clone()
#             first.composite(img.sequence[-1], 0, 0)
#             output.sequence.append(first)
#             output.sequence.extend(reversed(img.sequence[:-1]))
#             output.save(file=b)
#
#     image_bytes = b.getvalue()
#     key = 'reversed.' + str(time.time()) + '.gif'
#     try:
#         s3.put_object(ACL='private', Bucket=bucket_name, Key=key, Body=image_bytes, ContentType='image/gif')
#     except ConnectionError:
#         return "Sorry, I couldn't upload your jif to S3 :("
#
#     # return URL
#     return 'https://s3.amazonaws.com/{}/{}'.format(bucket_name, key)
