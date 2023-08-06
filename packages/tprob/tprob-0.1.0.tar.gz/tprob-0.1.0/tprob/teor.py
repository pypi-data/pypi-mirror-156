import os
def create_folder():
    if os.path.exists("pytemp"):
        pass
    else:
        os.mkdir("pytemp")

def download_file(url, local_filename):
    create_folder()
    import requests
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open('pytemp/' + local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return 'pytemp/' + local_filename

def download_ftp(local, filename):
    create_folder()
    from ftplib import FTP
    ftp = FTP('83.220.175.101')
    ftp.login("terver", 'qwerty1')
    ftp.cwd('files/')
    with open('./pytemp/' + local, 'wb') as fp:
        ftp.retrbinary('RETR ' + filename, fp.write)
    return './pytemp/' + local

def get_lecture():
    names = ['1) Файл лекции',
            '2) Точечные оценки',
            '3) Доверительное оценивание',
            '4) Общая схема проверки',
            '5) Проверка гипотезы об определенном значении параметров',
            '6) Сравнение генеральных средних',
            '7) Сравнение дисперсий двух',
            '8) Элементы дисперсионного анализа',
            '9) Критерий согласия'
            ]

    lectures = {
        "1": "lectures/lektsii.pdf",
        "2": "lectures/MS_Lecture_5_PM2022_8_04_2022.pdf",
        "3": "lectures/MS_Lecture_6_PM2022_15_04_2022.pdf",
        "4": "lectures/MS_Lecture_7_PM2022_6_05_2022_1.pdf",
        "5": "lectures/MS_Lecture_8_From_13_05_2022_PM2022_1.pdf",
        "6": "lectures/MS_Lecture_9_PM2022_13_05_2022.pdf",
        "7": "lectures/MS_Lecture_10_PM2022_20_05_2022.pdf",
        "8": "lectures/MS_Lecture_11_PM2022_27_05_2022.pdf",
        "9": "lectures/MS_Lecture_12_for_PM2022_3_06_2022__kopia.pdf",
    }

    for i in names:
        print(i)

    lec = input("Номер лекции: ")

    filepath = download_ftp('lec'+lec+".pdf", lectures[lec])

    from IPython.display import IFrame, display
    
    return IFrame(filepath, width=700, height=400)
