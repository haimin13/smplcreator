import csv
import os

location = '"/storage/emulated/0/Music/음악/'
playlistName = "플레이리스트 002"
start = '{"members":[\n'
end = '],"name":"'+playlistName+'","recentlyPlayedDate":0,"sortBy":4,"version":1}'

'''file_path = r'D:\음악\음악' #파일 이름 변경용
file_list = os.listdir(file_path)
for name in file_list:
    src = os.path.join(file_path, name)
    dst = os.path.join(file_path, name.replace(' - ','; '))
    os.rename(src, dst)'''
    
newNum = 0
num = 0
os.chdir("C:\\Users\\Hamin\\OneDrive - 고려대학교")
with open('음악DB.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    num = len(list(reader))
    
with open('음악DB.csv', 'a', newline='', encoding='utf-8') as f:
    isAdd = input("새로운 파일을 등록하시겠습니까?(y/n): ")
    if isAdd == 'y':
        regDate = input("날짜를 입력하세요(YYYY-MM-DD hh:mm): ")
        newNum = int(input("파일의 개수를 입력하세요: "))
        writer = csv.writer(f)
        for i in range(newNum):
            fileName = input("파일 이름을 입력하세요: ")
            fileInfo = fileName.split('; ')
            artist = fileInfo[0]
            title = fileInfo[1][:-4]
            fileExt = fileInfo[1][-4:]
            writer.writerow([artist, title, fileExt, regDate, num])
            num += 1
print(f'등록된 음악 수: {num-1}\n')
with open('음악DB.csv', 'r', encoding='utf-8') as f:
    with open(playlistName+'.smpl', 'w', encoding='utf-8') as smpl:
        smpl.write(start)
        reader = csv.reader(f)
        fileList = list(reader)
        i = 0
        for row in range(-1,-num,-1):
            content = '{"artist":"'+fileList[row][0]+'","info":' + location + fileList[row][0] + '; ' + fileList[row][1] + fileList[row][2] + '","order":' + str(i) + ',"title":"'+fileList[row][1]+'","type":65537},'
            i += 1
            if i == (num - 1):
                content = content.rstrip(',')
            smpl.write(content)
            smpl.write('\n')
        smpl.write(end)

print("플레이 리스트가 생성되었습니다.")