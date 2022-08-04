import boto3,botocore
import random
import argparse
from pprint import pprint

parser = argparse.ArgumentParser()


#コマンドライン引数を読み込む
parser.add_argument("--execute", help="optional", action="store_true")
parser.add_argument("--profile", help="optional", type=str)
parser.add_argument("--snapshot", help="optional", type=str)
args = parser.parse_args()
execute =None
pprint(args)

# オプション'execute'を処理
execute = not args.execute
print(f'execute = {execute}')
# オプション'profile'を処理
profile = args.profile if args.profile else 'tb_test'
# オプション'profile'を処理
snapshot = args.snapshot if args.snapshot else None

#EC2クライアントを作成
_session = boto3.Session(profile_name=profile)
ec2 = _session.client('ec2')

def main():
    #全ボリューム一覧を取得
    volumes = ec2.describe_volumes()
    # 未使用ボリュームを抽出
    if snapshot is None:
        volumes = [_v for _v in volumes['Volumes'] if not _v['Attachments']]
    else:
        volumes = [_v for _v in volumes['Volumes'] if not _v['Attachments'] and _v['SnapshotId']==snapshot]
    count = 0

    for volume in volumes:
        count += 1
        v = volume['VolumeId']
        try:
            print(f'count={count} trying volume={v} DryRun={execute}')
            ec2.delete_volume(VolumeId=v, DryRun=execute)

        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'DryRunOperation':
                print(e.response['Error'])
            else:
                raise e

if __name__ == '__main__':
    main()
