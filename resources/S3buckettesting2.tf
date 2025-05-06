resource "aws_s3_bucket" "example" {
provider = aws.bucket_region
name = "S3buckettesting2"
acl = "public"
}
