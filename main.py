# -*- coding: utf-8 -*-
import os
from multiprocessing import Pool
from pathlib import Path
import cv2
from tqdm import tqdm
from argparse import ArgumentParser
from utils import *


def _avi_extract(data):
    every_ms = 200
    file = Path(data[0])
    clip_path = Path(data[1])

    video_capture = cv2.VideoCapture(str(file))
    frame_count = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    count = 0
    good = True
    while good and count * fps * every_ms / 1000 <= frame_count:
        video_capture.set(cv2.CAP_PROP_POS_MSEC, (count * every_ms))
        good, image = video_capture.read()
        out = clip_path / "{}.jpg".format(count)
        if (not out.exists()) and good:
            img_r = cv2.resize(image, (640, 360))
            cv2.imwrite(out.as_posix(), img_r)
        count += 1
    video_capture.release()


def extract_frames(clip_folder, frame_root, pool_size=None):
    avis = sorted(list(clip_folder.glob("*/*.avi")), key=natural_keys_obj)
    frame_folders = sorted(list(set([frame_root / a.parent.name / a.stem for a in avis])))
    for f in frame_folders:
        f.mkdir(parents=True, exist_ok=True)
    data = list(zip(avis, frame_folders))
    if pool_size is None:
        pool_size = os.cpu_count()
    pool = Pool(pool_size)
    for _ in tqdm(pool.imap_unordered(_avi_extract, data), total=len(avis), desc='Extracting frames'):
        pass


def process():
    root = Path(args.lsmdc)
    assert root.exists(), "Please download LSMDC dataset in the same folder as this script"

    # Move movie clips to clips folder
    avis = list(root.glob("*/*.avi"))
    to_move = list(set([a.parent for a in avis]))
    for m in tqdm(to_move, desc='Moving clips'):
        m.rename(path_clips / m.name)

    # extracting frames with resolution 640*360
    extract_frames(path_clips, path_frames)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--lsmdc', default='LSMDC', type=str, help='LSMDC folder')
    args = parser.parse_args()

    path_base = Path(__file__).resolve().parent
    path_clips = Path(args.lsmdc) / "clips"
    path_frames = Path(args.lsmdc) / "frames"
    path_clips.mkdir(exist_ok=True)
    path_frames.mkdir(exist_ok=True)

    # data
    path_data = path_base / "data"
    path_meta = path_data / 'meta.csv'
    path_df = path_data / "df.csv"
    path_group = path_data / "group.csv"
    path_lsmdc = path_data / "lsmdc.json"

    process()
