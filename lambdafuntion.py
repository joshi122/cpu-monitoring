import boto3
import datetime
import csv

# AWS Clients
ses = boto3.client('ses', region_name='us-east-1')
s3 = boto3.client('s3')

# ✅ Your verified email
SENDER = "joshisudarshan068@gmail.com"
RECIPIENT = "joshisudarshan068@gmail.com"

# ✅ S3 bucket
BUCKET_NAME = "monitorlogs-cpu"

# ✅ EC2 Instances
instances = [
    {"id": "i-0f7a6843b8a2179d2", "name": "monitor01", "region": "us-east-1"},
    {"id": "i-08e8dfda06c1aa11d", "name": "monitor02", "region": "us-east-1"},
    {"id": "i-06b445fd4f999896b", "name": "monitor03", "region": "us-east-1"}
]

def lambda_handler(event, context):
    end = datetime.datetime.utcnow()
    start = end - datetime.timedelta(minutes=10)  # 🔥 recent data for testing

    report_data = []
    html_rows = ""
    high_cpu_found = False

    for inst in instances:
        cw = boto3.client('cloudwatch', region_name=inst["region"])

        response = cw.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'InstanceId', 'Value': inst["id"]}],
            StartTime=start,
            EndTime=end,
            Period=300,  # 5 minutes
            Statistics=['Average', 'Maximum', 'Minimum']
        )

        if response['Datapoints']:
            # Get latest datapoint
            data = sorted(response['Datapoints'], key=lambda x: x['Timestamp'])[-1]

            avg = round(data.get('Average', 0), 2)
            maxv = round(data.get('Maximum', 0), 2)
            minv = round(data.get('Minimum', 0), 2)
        else:
            avg = maxv = minv = 0

        # Status logic
        status = "OK"
        color = "#c6efce"

        if maxv > 40:
            status = "HIGH CPU 🚨"
            color = "#ffc7ce"
            high_cpu_found = True

        # CSV data
        report_data.append([
            inst["name"], inst["id"], inst["region"], avg, maxv, minv, status
        ])

        # HTML rows
        html_rows += f"""
        <tr>
            <td>{inst['name']}</td>
            <td>{inst['id']}</td>
            <td>{inst['region']}</td>
            <td>{avg}</td>
            <td>{maxv}</td>
            <td>{minv}</td>
            <td style='background-color:{color}'>{status}</td>
        </tr>
        """

    # 🔹 Save CSV
    file_name = f"/tmp/cpu_report_{end.strftime('%Y-%m-%d_%H-%M')}.csv"

    with open(file_name, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name","InstanceId","Region","AvgCPU","MaxCPU","MinCPU","Status"])
        writer.writerows(report_data)

    # 🔹 Upload to S3
    s3_key = f"alerts/cpu_report_{end.strftime('%Y-%m-%d_%H-%M')}.csv"
    s3.upload_file(file_name, BUCKET_NAME, s3_key)

    # 🔹 HTML Email
    html_body = f"""
    <html>
    <body>
    <h2>🚨 EC2 CPU Alert Report</h2>
    <table border="1" cellpadding="10" cellspacing="0">
        <tr style="background-color:#333;color:white;">
            <th>Name</th>
            <th>InstanceId</th>
            <th>Region</th>
            <th>Avg CPU</th>
            <th>Max CPU</th>
            <th>Min CPU</th>
            <th>Status</th>
        </tr>
        {html_rows}
    </table>
    <br>
    <p><b>Generated:</b> {end}</p>
    <p><b>S3 File:</b> {BUCKET_NAME}/{s3_key}</p>
    </body>
    </html>
    """

    # 🔥 SEND EMAIL ONLY IF CPU > 70%
    if high_cpu_found:
        ses.send_email(
            Source=SENDER,
            Destination={'ToAddresses': [RECIPIENT]},
            Message={
                'Subject': {'Data': '🚨 HIGH CPU ALERT - EC2'},
                'Body': {'Html': {'Data': html_body}}
            }
        )
        return "🚨 Alert sent (High CPU detected)"

    else:
        return "✅ No high CPU - No email sent"