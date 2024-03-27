import argparse

# argparse를 사용하여 명령행 인자 파싱
parser = argparse.ArgumentParser(description='옵션 설명')
group = parser.add_mutually_exclusive_group(required=True)

group.add_argument('-m', '--member_key', type=int, help='member key')
group.add_argument('-p', '--playlist_key', type=int, help='playlist key')

args = parser.parse_args()

if args.member_key:
    print('member_key', args.member_key)

if args.playlist_key:
    print('playlist_key', args.playlist_key)
