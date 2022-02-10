import os.path as pth
from moviepy.editor import VideoFileClip

root = pth.join('D:', 'Волейбол', 'Тренировки с Формикой')
folder_to_save = 'Highlights'

def cut_and_save_subclip(local_address, save_name, start=0, end=None):  # local adress must describe position after root
    try:
        with VideoFileClip(local_address) as clip:
            cut = clip.subclip(start, end)
            cut.write_videofile(pth.join(root, folder_to_save, save_name))
    except Exception as e:
        print(e)