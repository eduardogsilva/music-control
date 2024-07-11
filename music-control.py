#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import subprocess
import os

# Função para criar uma imagem de placeholder
def create_placeholder_image(size, color=(200, 200, 200)):
    img = Image.new('RGB', size, color)
    return ImageTk.PhotoImage(img)

# Função para obter o volume atual do sistema
def get_system_volume():
    try:
        # Corrigir o comando para capturar o volume corretamente
        default_sink = subprocess.check_output(
            "pactl info | grep 'Default Sink' | awk '{print $3}'",
            shell=True
        ).decode("utf-8").strip()

        volume_output = subprocess.check_output(
            f"pactl list sinks | grep -A 15 '{default_sink}' | grep '^[[:space:]]Volume:' | head -n 1 | awk '{{print $5}}'",
            shell=True
        ).decode("utf-8").strip()

        volume_percentage = int(volume_output.strip('%'))
        return volume_percentage
    except subprocess.CalledProcessError:
        return 0

# Função para ajustar o volume do sistema
def set_system_volume(volume):
    subprocess.call(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{volume}%"])

# Função chamada quando o slider de volume é ajustado
def volume_changed(event):
    new_volume = volume_slider.get()
    set_system_volume(new_volume)

# Função para atualizar as informações da música atual e o volume
def update_song_info():
    try:
        song_title = subprocess.check_output(["playerctl", "metadata", "title"]).decode("utf-8").strip()
        song_artist = subprocess.check_output(["playerctl", "metadata", "artist"]).decode("utf-8").strip()
        album_name = subprocess.check_output(["playerctl", "metadata", "album"]).decode("utf-8").strip()
        song_art_url = subprocess.check_output(["playerctl", "metadata", "mpris:artUrl"]).decode("utf-8").strip()

        label_song.config(text=f"Title: {song_title}")
        label_artist.config(text=f"Artist: {song_artist}")
        label_album.config(text=f"Album: {album_name}")

        if song_art_url.startswith('file://'):
            song_art_path = song_art_url[7:]  # Remove o prefixo 'file://'
            if os.path.exists(song_art_path):
                img = Image.open(song_art_path)
                img = img.resize((100, 100), Image.LANCZOS)
                img = ImageTk.PhotoImage(img)
                label_image.config(image=img)
                label_image.image = img
            else:
                label_image.config(image=placeholder_image)
                label_image.image = placeholder_image
        else:
            label_image.config(image=placeholder_image)
            label_image.image = placeholder_image
    except subprocess.CalledProcessError:
        label_song.config(text="Title: Not Playing")
        label_artist.config(text="Artist: Not Available")
        label_album.config(text="Album: Not Available")
        label_image.config(image=placeholder_image)
        label_image.image = placeholder_image

    # Atualizar o volume do slider
    current_volume = get_system_volume()
    volume_slider.set(current_volume)

    # Atualizar a cada 5 segundos
    root.after(5000, update_song_info)

# Funções para os controles de áudio
def play_pause():
    try:
        subprocess.call(["playerctl", "play-pause"])
    except subprocess.CalledProcessError:
        pass

def next_song():
    try:
        subprocess.call(["playerctl", "next"])
    except subprocess.CalledProcessError:
        pass

def previous_song():
    try:
        subprocess.call(["playerctl", "previous"])
    except subprocess.CalledProcessError:
        pass

# Criar a janela principal
root = tk.Tk()
root.title("Music Player")
root.geometry("500x175")
root.resizable(True, False)
#root.attributes('-topmost', True)
#root.overrideredirect(True)

# Criar imagem de placeholder
placeholder_image = create_placeholder_image((100, 100))

# Frame principal
frame_main = ttk.Frame(root)
frame_main.pack(pady=10, padx=10, fill='x')

# Informações da música
label_image = ttk.Label(frame_main, image=placeholder_image)
label_image.grid(row=0, column=0, rowspan=3, padx=(0, 10), pady=5, sticky='w')

text_frame = ttk.Frame(frame_main)
text_frame.grid(row=0, column=1, rowspan=3, sticky='w')

label_song = ttk.Label(text_frame, text="Title: Not Playing", font=("Helvetica", 12), anchor='w', width=40)
label_song.grid(row=0, column=0, sticky='w', pady=(0, 20))

label_artist = ttk.Label(text_frame, text="Artist: Not Available", font=("Helvetica", 12), anchor='w', width=40)
label_artist.grid(row=1, column=0, sticky='w', pady=(2, 20))

label_album = ttk.Label(text_frame, text="Album: Not Available", font=("Helvetica", 12), anchor='w', width=40)
label_album.grid(row=2, column=0, sticky='w', pady=(2, 0))

# Controles de áudio
frame_controls = ttk.Frame(frame_main)
frame_controls.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky='w')

btn_previous = ttk.Button(frame_controls, text="Previous", command=previous_song)
btn_previous.grid(row=0, column=0, padx=5)

btn_play_pause = ttk.Button(frame_controls, text="Play/Pause", command=play_pause)
btn_play_pause.grid(row=0, column=1, padx=5)

btn_next = ttk.Button(frame_controls, text="Next", command=next_song)
btn_next.grid(row=0, column=2, padx=5)

# Slider de volume
style = ttk.Style()
style.configure("TScale", troughcolor='grey', sliderthickness=15)

volume_slider = ttk.Scale(frame_controls, from_=0, to=100, orient='horizontal', command=volume_changed, style="TScale")
volume_slider.grid(row=0, column=3, padx=5)
volume_slider.set(get_system_volume())

# Iniciar a atualização das informações da música
update_song_info()

# Iniciar o loop principal da interface gráfica
root.mainloop()
