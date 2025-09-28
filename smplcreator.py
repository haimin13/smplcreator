import warnings
import os
import pandas as pd
from pyuca import Collator
from datetime import datetime

warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)


def compare_db_and_file():
    pc_list = os.listdir(pc_dir)
    pc_data = pd.DataFrame(pc_list, columns=["fileName"])

    pc_len = len(pc_data)
    db_len = len(db_data)
    identity = True
    
    print("\n실제 파일과 DB의 항목을 비교합니다.")
    print(f"\n파일 수: {pc_len}, DB 항목 수: {db_len}")
    
    db_data["fileName"] = db_data["artist"] + '; ' + db_data["title"] + db_data["fileExt"]  # 텍스트 정렬을 위해 임시로 새로운 열을 만들어줌
    db_data.sort_values(by="fileName", key = lambda x: x.map(collator.sort_key), inplace=True)  # 윈도우 파일 탐색기 정렬 기준과 동일하게 정렬
    pc_data.sort_values(by="fileName", key = lambda x: x.map(collator.sort_key), inplace=True)

    db_data.to_csv(db_temp_csv, index=False)    # 디버깅용 임시파일
    pc_data.to_csv(pc_temp_csv, index=False)    # 디버깅용 임시파일
    
    
    i, j = (0, 0)
    print(div_line)
    while (i < pc_len or j < db_len):
        pc_entry = pc_data.iloc[i].loc["fileName"]
        db_entry = db_data.iloc[j].loc["fileName"]
        if (pc_entry != db_entry):
            identity = False
            if (not pc_data["fileName"].isin([db_entry]).any()):
                print(f"실제 파일에 \"  {db_entry}  \"가 존재하지 않습니다.")
                i -= 1
            else:
                print(f"DB에 \"  {pc_entry}  \"가 존재하지 않습니다.")
                j -= 1
        i += 1
        j += 1 

    if (identity):
        print("일치합니다.")
    # i나 j가 len에 도달하지 못하고 종료되었을 때
    while (i < pc_len): 
        print(f"pc_len = {pc_len}, i = {i}")
        pc_entry = pc_data.iloc[i].loc["fileName"]
        print(f"실제 파일에 \"  {db_entry}  \"가 존재하지 않습니다.")
        i += 1
    while (j < db_len):
        print(f"db_len = {db_len}, j = {j}")
        db_entry = db_data.iloc[j].loc["fileName"]
        print(f"DB에 \"  {pc_entry}  \"가 존재하지 않습니다.")
        j += 1

    db_data.drop(columns=["fileName"], inplace=True) # 비교에 사용한 임시 열 제거
    print(div_line + "\n검사가 완료되었습니다.\n")

    return False


def add():
    global db_data
    db_len = len(db_data)
    newNum = int(input("파일의 개수를 입력하세요: "))
    regDate = input("날짜를 입력하세요(YYYY-MM-DD hh:mm): ")
    if (regDate == ""): 
        regDate = datetime.now().strftime("%Y-%m-%d %H:%M")
        print("현재 시간을 적용합니다.")

    i = 0
    while (i < newNum):
        file_name = input("파일 이름을 입력하세요: ")
        is_valid, artist, title, file_ext = extract_data(file_name)
        if (not is_valid): continue
        new_row = pd.DataFrame({"artist":[artist], "title": [title], "fileExt": [file_ext], "regDate": [regDate],
                               "regNo": [db_len]})
        db_data = pd.concat([db_data, new_row], ignore_index=True)
        i += 1

    return False

def add_auto():
    global db_data
    db_len = len(db_data)
    file_list = os.listdir(add_dir)
    regDate = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"파일 개수: {len(file_list)}")
    print(f"등록 시간: {regDate}")
    for i in range(len(file_list)):
        is_valid, artist, title, file_ext = extract_data(file_list[i])
        if (not is_valid): 
            print(f"다음 파일 등록이 실패하였습니다: {file_list[i]}")
            continue
        new_row = pd.DataFrame({"artist":[artist], "title": [title], "fileExt": [file_ext], "regDate": [regDate],
                               "regNo": [db_len + i]})
        db_data = pd.concat([db_data, new_row], ignore_index=True)

    return False


def delete(file_name):
    global trash_can

    is_valid, artist, title, file_ext = extract_data(file_name)
    if (not is_valid): return

    index = db_data[(db_data["artist"] == artist) & (db_data["title"] == title) & (db_data["fileExt"] == file_ext)].index
    print(div_line)
    try: 
        os.remove(pc_dir + '/' + file_name)
        print(f"{file_name}파일이 제거되었습니다.")
    except FileNotFoundError as e:
        print(div_line, e, div_line)

    if ((db_data["artist"] == artist) & (db_data["title"] == title)).any():
        popped_row = db_data.iloc[index[0]] # DB에서 삭제할 데이터 추출
        db_data.drop(index[0], inplace = True) # DB에서 해당 데이터 삭제
        popped_row.drop("regNo", axis=0, inplace=True)  # regNo feature 필요없으니 제거
        popped_row.loc["Wave"] = wave
    
        trash_can = pd.concat([trash_can, popped_row.to_frame().T], axis=0, ignore_index = True)
        print(f"{file_name}이 DB에서 제거되었습니다.")

    print(div_line)
    return False


def extract_data(file_name):
    file_data = file_name.split('; ')

    if (len(file_data) < 2):
        print("파일명 형식이 잘못되었습니다.")
        return (False, None, None, None)
    
    artist = file_data[0]
    title = file_data[1][:-4]
    file_ext = file_data[1][-4:]

    return (True, artist, title, file_ext)


def create_smpl():
    with open (playlist_name+ ".smpl", 'w', encoding = "utf-8") as smpl:
        db_len = len(db_data)
        smpl.write(prefix)
        for i in range(db_len):
            artist = db_data.iloc[-(i+1), 0]
            title = db_data.iloc[-(i+1), 1]
            file_ext = db_data.iloc[-(i+1), 2]
            content = ('{"artist":"' + artist + '","info":' + phone_dir + artist + '; ' + title + file_ext + 
                       '","order":' + str(i) + ',"title":"' + title + '","type":65537},')
            if i == (db_len - 1):
                content = content.rstrip(',')
            smpl.write(content)
            smpl.write("\n")
        smpl.write(postfix)
    print("\n플레이리스트가 생성되었습니다.\n")


def rearrange():
    db_data.sort_values(by=["regDate","artist","title"], key = lambda x: x.map(collator.sort_key), inplace=True)
    return False


def renumber():
    for i in range(len(db_data)):
        db_data.iloc[i,4] = i+1
    return False


def save():
    if (db_data is not None):
        rearrange()
        renumber()
        create_smpl()
        db_data.to_csv(db_dir, index=False)
        trash_can.to_csv(del_dir, index=False)

        print("저장이 완료되었습니다.")
        return True
    else:
        print("저장이 실패했습니다.")
        return False


def custom():
    {}
        

# 검색기능 추가 요망

code_path = os.path.dirname(os.path.realpath(__file__))
db_dir = code_path + "\\음악DB.csv"
del_dir = code_path + "\\db_del.csv"
pc_dir = "D:/음악/음악"
add_dir = code_path + "\\확정"
db_temp_csv = code_path + "\\sorted_음악DB.csv"
pc_temp_csv = code_path + "\\sorted_pc_data.csv"
div_line = "\n========================================\n"
help = """
    quit - 프로그램을 종료합니다.
    compare - 실제 파일과 DB의 항목을 비교합니다.
    del [삭제할 파일] - DB에 있을 경우 DB에서 제거합니다. DB에 없을 경우 파일을 제거합니다.
    add - DB에 항목을 추가합니다.
    save - 지금까지의 변경사항을 DB파일에 저장합니다.
    renumber - 현재 db 순서대로 regNo를 재지정합니다.
    rearrange - regNo, artist, title을 비교하여 항목 순서를 재정렬합니다.
    custom - 코드 상에서 정의한 함수를 실행합니다.
    """

phone_dir = '"/storage/emulated/0/Music/음악/'
playlist_dir = "하민의 Galaxy Note20 5G/내장 저장공간/SamsungMusic/Playlists/" #안됨
playlist_name = "플레이리스트 002"
prefix = '{"members":[\n'
postfix = '],"name":"'+playlist_name+'","recentlyPlayedDate":0,"sortBy":4,"version":1}'

collator = Collator()
is_saved = True

db_data = pd.read_csv(db_dir)
trash_can = pd.read_csv(del_dir)
wave = trash_can.iloc[-1,-1]


while (True):
    command = input(">>>명령을 입력하세요(help - 명령어 목록): ")
    if command == "quit":
        if not is_saved:
            while (True):
                saving = input("변경 사항이 저장되지 않았습니다. 저장하시겠습니까? (y/n):")
                if saving.casefold() == "y":
                    save()
                    break
                elif saving.casefold() == "n":
                    break
                else:
                    print("입력이 올바르지 않습니다.")
        break
        
    elif command == "save":
        is_saved = save()
    elif command == "help":
        print(div_line + help + div_line)
    elif command == "compare":
        is_saved = compare_db_and_file()
    elif command[:3] == "del":
        is_saved = delete(command[4:])
    elif command == "add":
        is_saved = add()
    elif command == "renumber":
        is_saved = renumber()
    elif command == "rearrange":
        is_saved = rearrange()
    elif command == "custom":
        custom()

    elif command == "addauto":
        add_auto()
    

# 