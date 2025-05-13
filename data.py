import json
import os
import datetime 

FILENAME = "game_history.json"
MAXLAST = 100 # Lưu lịch sử của 100 trận gần nhất

def load_game_history(filename=FILENAME):
    """
    Tải lịch sử trò chơi từ tệp JSON.

    Tham số:
        filename (str): Đường dẫn đến tệp JSON chứa lịch sử trò chơi.

    Trả về:
        list: Danh sách các từ điển đại diện cho kết quả các ván chơi trước đó, 
            bao gồm 'result','time','difficulty'
    """
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            history = json.load(f)
            return history   
    return []

def save_game_history(history_list, filename=FILENAME):
    """
    Lưu lịch sử trò chơi vào tệp JSON.

    Tham số:
        history_list (list): Danh sách các từ điển chứa kết quả các ván chơi.
        filename (str): Đường dẫn đến tệp JSON để lưu lịch sử trò chơi.
    """
    with open(filename, 'w') as f:
        json.dump(history_list, f, ensure_ascii=False, indent=4)
        
def add_game_result(result_string, difficulty):
    """
    Thêm một kết quả trò chơi mới vào lịch sử và lưu lại.

    Tham số:
        result_string (str): Kết quả của ván chơi (ví dụ: "win", "lose").
        difficulty (str): Mức độ khó của ván chơi.

    Ghi chú:
        Chỉ giữ lại tối đa 100 kết quả gần nhất trong lịch sử.
    """
    current_history = load_game_history() 
    game_record = {
        'result': result_string,
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
        'difficulty': difficulty
    }

    current_history.append(game_record) 

    if len(current_history) > 10:
        current_history.pop()

    save_game_history(current_history) 
