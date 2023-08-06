import argparse
from pathlib import Path
from datetime import datetime


# Прийняття даних з консолі
def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', type=str,
                        help='argument "folder" should be a name of folder where placed files with datas', default='')
    parser.add_argument("--asc", help="sort by first to last ", action="store_false")
    parser.add_argument("--desc", help="sort by last to first", action="store_true")
    parser.add_argument("--driver", help="information about the pilot, enter the name in ' '")
    return parser.parse_args()


class Report:
    def __init__(self, folder):
        self.folder = folder
        self.pilots_list = []
        self.start_time_list = []
        self.end_time_list = []


    # Зчитування даних з файлів
    def work_with_file(self):
        try:
            with Path(Path.cwd().parents[1], self.folder, 'abbreviations.txt').open(encoding='utf-8') as f:
                self.pilots_list = [line.strip().split('_') for line in f.readlines() if line.strip() != '']
        except FileNotFoundError:
            raise FileNotFoundError('File abbreviations.txt not found')
        try:
            with Path(Path.cwd().parents[1], self.folder, 'start.log').open() as f:
                self.start_time_list = [line.strip().split('_') for line in f.readlines() if line.strip() != '']
        except FileNotFoundError:
            raise FileNotFoundError('File start.log not found')
        try:
            with Path(Path.cwd().parents[1], self.folder, 'end.log').open() as f:
                self.end_time_list = [line.strip().split('_') for line in f.readlines() if line.strip() != '']
        except FileNotFoundError:
            raise FileNotFoundError('File end.log not found')


    # Створення словника з даними про пілотів
    def work_with_pilots(self):
        pilots_info = {}
        for i in self.pilots_list:
            pilots_info[i[0]] = [i[1], i[2]]
        return pilots_info


    # Оброблення інформації початок та кінець найкращих кіл. Створення списку списків абрівіатур пилотів та часу
    # найкращого кола [[абрівіатура, час] ....]
    def work_with_time(self):
        self.start_time_list.sort()
        self.end_time_list.sort()
        time_best_lap = []
        sort_flag = False
        for i in range(len(self.start_time_list)):
            if self.start_time_list[i][0][0:3] == self.end_time_list[i][0][0:3]:
                pilot = self.start_time_list[i][0][0:3]
            else:
                pilot = None
            time_start = datetime.strptime(self.start_time_list[i][1], "%H:%M:%S.%f")
            time_end = datetime.strptime(self.end_time_list[i][1], "%H:%M:%S.%f")
            if (time_end - time_start).days < 0:
                lap_time = time_start - time_end
            else:
                lap_time = time_end - time_start

            time_best_lap.append([pilot, str(lap_time).lstrip('0:0').replace("000", "")])
        if arguments.desc:
            sort_flag = True
        time_best_lap.sort(key=lambda x: x[1], reverse=sort_flag)
        return time_best_lap

# Підготовка даних до виводу. Якщо користувач вводить інформацію про якогось пілота, то інформація буде виводитись тільки про нього.
# В іншому випадку буде виводитися загальна таблиця результатів. За замовчуванням порядку виводу інформації - від
# кращого результату до гіршого, але за бажанням користувач порядок виводу моде бути змінений на зворотній.
# Результатом функції є список який передається на друк
def build_report(time_list, pilot_list):
    list_to_print = []
    if bool(arguments.driver):
        if list(filter(lambda x: arguments.driver in x, pilot_list.values())):
            for key, value in pilot_list.items():
                if arguments.driver in value:
                    time_one_pilot = [x[1] for x in time_list if x[0] == key]
                    list_to_print.append([pilot_list[key][0], pilot_list[key][1], time_one_pilot[0]])
        else:
            print("name is incorrect, put correct name")
    else:
        for i in range(len(time_list)):
            list_to_print.append([pilot_list[time_list[i][0]][0], pilot_list[time_list[i][0]][1], time_list[i][1]])
    print_report(list_to_print)

# Вивід даних
def print_report(print_list):
    for id, value in enumerate(print_list, start=1):
        print(f'{id:2}. {value[0]:18} | {value[1]:25} | {value[2]}')
        if id == 15:
            print("-" * 62)


if __name__ == '__main__':
    arguments = args_parser()
    report = Report(arguments.folder)
    report.work_with_file()
    build_report(report.work_with_time(), report.work_with_pilots())
