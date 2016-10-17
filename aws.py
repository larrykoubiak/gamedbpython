import boto3

s3 = boto3.resource('s3')
bucket = s3.Bucket('gamefaqs')
key = bucket.download_file('3DO/3D Atlas (US)-45033_back.jpg','test/3D Atlas (US)-45033_back.jpg')
