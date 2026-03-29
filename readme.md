**Automating the cpu utilization report using aws**

**Step 1 – create 3 instances with linux and launch instances.**

**Step 2- create s3 bucket by unique name cpu-report.**

**Step3 – create ses email and verify you email by creating identity .**

**Step4- create iam role with the naem cpu report-role and give all three permsiions**

**AmazonS3FullAccess and AmazonSNSFullAccess and CloudWatchReadOnlyAccess and SESAccessPolicy.**

**Step5- create lambda function with python3.11 and in role select your created role.**

**Add in code section** 



**add you email and arn and s3 bucket name, and create new test event and deploy and test.** 

**Step6- create aws eventbridge sheduler create schedule rate 2 days** 

**Recurring g schedule and rate based schedule in target select lambda and select your lambda function  already created.**





**In threshold vale set as per the requirement and at last all the report file will get store in s3 bucket you created.**





**This is the process of fully automating cpu utilzation report.**



