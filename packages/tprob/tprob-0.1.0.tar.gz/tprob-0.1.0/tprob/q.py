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


def show_q1_1():
    from IPython.display import IFrame, display
    q1 = 'https://cdn.discordapp.com/attachments/723645902723612763/988751070287253534/Q1-1-23.pdf'
    filepath = download_file(q1, 'q1-1.pdf')
    return IFrame(filepath, width=700, height=400)

def show_q1_2():
    from IPython.display import IFrame, display
    q1 = 'https://cdn.discordapp.com/attachments/723645902723612763/988751070849302528/Q1-24-44.pdf'
    filepath = download_file(q1, 'q1-2.pdf')
    return IFrame(filepath, width=700, height=400)


def show_q2_1():
    from IPython.display import IFrame, display
    q1 = 'https://cdn.discordapp.com/attachments/723645902723612763/989126736421732402/Q2-1-26.pdf'
    filepath = download_file(q1, 'q1-2.pdf')
    return IFrame(filepath, width=700, height=400)

def show_q2_2():
    from IPython.display import IFrame, display
    q1 = 'https://cdn.discordapp.com/attachments/723645902723612763/989126737013145710/Q2-26-56.pdf'
    filepath =  download_file(q1, 'q1-2.pdf')
    return IFrame(filepath, width=700, height=400)


def show_q3_1():
    from IPython.display import IFrame, display
    q1 = 'https://cdn.discordapp.com/attachments/723645902723612763/989127050965180496/Q3.pdf'
    filepath =  download_file(q1, 'q1-2.pdf')
    return IFrame(filepath, width=700, height=400)

def show_google():
    from IPython.display import IFrame, display
    q1 = 'https://google.com/'
    return IFrame(q1, width=700, height=400)

def show_questions_1():
    from IPython.display import IFrame, display
    q1 = 'https://cdn.discordapp.com/attachments/723645902723612763/989130420010516520/ForStudOpen_MS_Exam_QuestionDemoVar_PM2022-1-20.pdf'
    filepath =  download_file(q1, 'q_1.pdf')
    return IFrame(filepath, width=700, height=400)

def show_questions_2():
    from IPython.display import IFrame, display
    q1 = 'https://cdn.discordapp.com/attachments/723645902723612763/989130420815802378/ForStudOpen_MS_Exam_QuestionDemoVar_PM2022-21-31.pdf'
    filepath = download_file(q1, 'q_2.pdf')
    return IFrame(filepath, width=700, height=400)