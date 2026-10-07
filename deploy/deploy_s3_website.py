"""
Deploy GENIUS Device Simulator to AWS S3 Static Website Hosting
"""

import os
import mimetypes
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")


def deploy():
    sts = boto3.client("sts")
    account_id = sts.get_caller_identity()["Account"]
    bucket_name = f"genius-simulator-{account_id}"

    s3 = boto3.client("s3", region_name=REGION)

    print(f"[*] Deploying GENIUS to AWS S3 Bucket: {bucket_name} in {REGION}...")

    # 1. Create Bucket
    try:
        if REGION == "us-east-1":
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": REGION}
            )
        print(f"[+] Bucket created: {bucket_name}")
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        if code in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
            print(f"[*] Bucket {bucket_name} already exists, proceeding...")
        else:
            raise e

    # 2. Disable Block Public Access for static website hosting
    s3.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": False,
            "IgnorePublicAcls": False,
            "BlockPublicPolicy": False,
            "RestrictPublicBuckets": False
        }
    )
    print("[+] Public access block disabled for website hosting.")

    # 3. Apply Bucket Policy for Public Read
    policy = f"""{{
        "Version": "2012-10-17",
        "Statement": [
            {{
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::{bucket_name}/*"
            }}
        ]
    }}"""
    s3.put_bucket_policy(Bucket=bucket_name, Policy=policy)
    print("[+] Public read policy applied.")

    # 4. Enable Website Hosting
    s3.put_bucket_website(
        Bucket=bucket_name,
        WebsiteConfiguration={
            "IndexDocument": {"Suffix": "index.html"},
            "ErrorDocument": {"Key": "index.html"}
        }
    )
    print("[+] S3 Website Hosting enabled.")

    # 5. Upload client files
    client_dir = os.path.join(os.path.dirname(__file__), "..", "client")
    for root, _, files in os.walk(client_dir):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, client_dir).replace("\\", "/")
            mime_type, _ = mimetypes.guess_type(full_path)
            if f.endswith(".js"):
                mime_type = "application/javascript"
            elif f.endswith(".css"):
                mime_type = "text/css"
            elif f.endswith(".html"):
                mime_type = "text/html"

            with open(full_path, "rb") as data:
                s3.put_object(
                    Bucket=bucket_name,
                    Key=rel_path,
                    Body=data,
                    ContentType=mime_type or "application/octet-stream"
                )
            print(f"  -> Uploaded client/{rel_path} ({mime_type})")

    # 6. Upload audio clips to clips/
    clips_dir = os.path.join(os.path.dirname(__file__), "..", "tests", "clips")
    if os.path.exists(clips_dir):
        for root, _, files in os.walk(clips_dir):
            for f in files:
                if f.endswith(".wav") or f.endswith(".json"):
                    full_path = os.path.join(root, f)
                    key = f"clips/{f}"
                    mime = "audio/wav" if f.endswith(".wav") else "application/json"
                    with open(full_path, "rb") as data:
                        s3.put_object(
                            Bucket=bucket_name,
                            Key=key,
                            Body=data,
                            ContentType=mime
                        )
                    print(f"  -> Uploaded {key} ({mime})")

    if REGION == "us-east-1":
        website_url = f"http://{bucket_name}.s3-website-us-east-1.amazonaws.com"
    else:
        website_url = f"http://{bucket_name}.s3-website.{REGION}.amazonaws.com"

    print("\n" + "=" * 70)
    print("[SUCCESS] GENIUS WEBSITE DEPLOYED SUCCESSFULLY TO AWS!")
    print(f"[URL] Live Website URL: {website_url}")
    print("=" * 70 + "\n")
    return website_url


if __name__ == "__main__":
    deploy()
