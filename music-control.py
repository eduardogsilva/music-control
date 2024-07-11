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

# Função para obter a duração da música
def get_song_duration():
    try:
        duration = subprocess.check_output(["playerctl", "metadata", "mpris:length"]).decode("utf-8").strip()
        duration_ms = int(duration) // 1000000  # Convertendo para segundos
        return duration_ms
    except subprocess.CalledProcessError:
        return 0

# Função para obter o progresso atual da música
def get_song_position():
    try:
        position = subprocess.check_output(["playerctl", "position"]).decode("utf-8").strip()
        position_s = int(float(position))  # Convertendo para segundos
        return position_s
    except subprocess.CalledProcessError:
        return 0

# Função para ajustar a posição da música
def set_song_position(position):
    subprocess.call(["playerctl", "position", str(position)])

# Função chamada quando a barra de progresso é ajustada
def progress_press(event):
    global progress_dragging
    progress_dragging = True

def progress_release(event):
    global progress_dragging
    progress_dragging = False
    new_position = progress_slider.get()
    if new_position == 0:
        new_position = 1  # Evitar que a música pare ao mover para o início
    set_song_position(new_position)

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

        # Atualizar a duração e o progresso da música
        song_duration = get_song_duration()
        song_position = get_song_position()
        progress_slider.config(to=song_duration)
        if not progress_dragging:
            progress_slider.set(song_position)

    except subprocess.CalledProcessError:
        label_song.config(text="Title: Not Playing")
        label_artist.config(text="Artist: Not Available")
        label_album.config(text="Album: Not Available")
        label_image.config(image=placeholder_image)
        label_image.image = placeholder_image
        progress_slider.set(0)

    # Atualizar o volume do slider
    current_volume = get_system_volume()
    volume_slider.set(current_volume)

    root.after(3000, update_song_info)

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
root.title("Music Control")
root.geometry("500x170")
root.resizable(True, False)

# Criar imagem de placeholder
placeholder_image = create_placeholder_image((100, 100))

# Frame principal
frame_main = ttk.Frame(root)
frame_main.pack(pady=10, padx=10, fill='x')

# Informações da música
label_image = ttk.Label(frame_main, image=placeholder_image)
label_image.grid(row=0, column=0, rowspan=4, padx=(0, 10), pady=(5, 0), sticky='nw')

text_frame = ttk.Frame(frame_main)
text_frame.grid(row=0, column=1, rowspan=1, sticky='nw')

label_song = ttk.Label(text_frame, text="Title: Not Playing", font=("Helvetica", 12), anchor='w', width=40)
label_song.grid(row=0, column=0, sticky='w', pady=(5, 0))

label_artist = ttk.Label(text_frame, text="Artist: Not Available", font=("Helvetica", 12), anchor='w', width=40)
label_artist.grid(row=1, column=0, sticky='w', pady=(5, 0))

label_album = ttk.Label(text_frame, text="Album: Not Available", font=("Helvetica", 12), anchor='w', width=40)
label_album.grid(row=2, column=0, sticky='w', pady=(5, 5))

# Sliders de progresso e volume lado a lado
sliders_frame = ttk.Frame(frame_main)
sliders_frame.grid(row=3, column=1, columnspan=1, sticky='ew', pady=(10, 0))

progress_slider = ttk.Scale(sliders_frame, from_=0, to=100, orient='horizontal')
progress_slider.pack(side='left', fill='x', expand=True, padx=(0, 5))
progress_slider.bind("<ButtonPress-1>", progress_press)
progress_slider.bind("<ButtonRelease-1>", progress_release)

volume_slider = ttk.Scale(sliders_frame, from_=0, to=100, orient='horizontal', command=volume_changed, style="TScale")
volume_slider.pack(side='left', fill='x', expand=True, padx=(5, 0))

# Controles de áudio
frame_controls = ttk.Frame(frame_main)
frame_controls.grid(row=4, column=0, columnspan=2, pady=(10, 0), sticky='w')

btn_previous = ttk.Button(frame_controls, text="⏪", command=previous_song)
btn_previous.grid(row=0, column=0, padx=5)

btn_play_pause = ttk.Button(frame_controls, text="▶️", command=play_pause)
btn_play_pause.grid(row=0, column=1, padx=5)

btn_next = ttk.Button(frame_controls, text="⏩", command=next_song)
btn_next.grid(row=0, column=2, padx=5)

progress_dragging = False

# Iniciar a atualização das informações da música
update_song_info()

# Iniciar o loop principal da interface gráfica
root.mainloop()
