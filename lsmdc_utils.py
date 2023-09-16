# -*- coding: utf-8 -*-
from __future__ import division
from pathlib import Path
import pandas as pd

from utils import *


def prepare_lsmdc_df(out_df, path_lsmdc_anno_train, path_lsmdc_anno_val, path_lsmdc_anno_test, path_meta):
    """

    :param out_df: The out path of the dataframe for lsmdc annotation summary
    :param path_lsmdc_anno_train: The path of the training annotation file
    :param path_lsmdc_anno_val: The path of the validation annotation file
    :param path_lsmdc_anno_test: The path of the test annotation file
    :param path_meta: The path of the meta file
    :return:
    """

    def time2s(t):
        h, m, s, ms = [int(x) for x in t.split(".")]
        s = ms / 1000 + s + m * 60 + h * 3600
        return s

    def rm_id(x):
        """
        remove id labels
        """
        x = re.sub(r'<PERSON>.*</PERSON>', 'SOMEONE', x)
        res = [r'SOMEONE<.+?>', r'SOMEONE\'s<.+?>', r'She<.+?>', r'she<.+?>', r'He<.+?>', r'he<.+?>']
        subs = ['SOMEONE', 'SOMEONE\'s', 'She', 'she', 'He', 'he']
        for idx, r in enumerate(res):
            while re.search(r, x):
                x = re.sub(r, subs[idx], x, 1)
        return x

    def rm_someone(x):
        """
        remove someone
        """
        x = x.replace('<PERSON>', '').replace('</PERSON>', '')
        res = [r'SOMEONE<.+?>', r'SOMEONE\'s<.+?>', r'She<.+?>', r'she<.+?>', r'He<.+?>', r'he<.+?>', r'HE<.+?>']
        left = ['SOMEONE<', 'SOMEONE\'s<', 'She<', 'she<', 'He<', 'he<', 'HE']
        for idx, r in enumerate(res):
            while re.search(r, x):
                x = re.sub(r, re.search(r, x).group(0).replace(left[idx], '', 1).replace('>', '', 1), x, 1)
        return x

    df_heads = ["clip", "start_aligned", "end_aligned", "start", "end", "sentence"]
    df_anno_train = pd.read_csv(path_lsmdc_anno_train, sep="\t", encoding="ISO-8859-1", names=df_heads)
    df_anno_val = pd.read_csv(path_lsmdc_anno_val, sep="\t", encoding="ISO-8859-1", names=df_heads)
    df_anno_test = pd.read_csv(path_lsmdc_anno_test, sep="\t", encoding="ISO-8859-1", names=df_heads)
    df = df_anno_train.append([df_anno_val], ignore_index=True)
    df = df.drop_duplicates()
    df["movie"] = df["clip"].apply(lambda x: x.split("_0")[0])
    df["movie_name"] = df["movie"].apply(lambda x: ' '.join(x.split('_')[1:]).replace('-', ' ').strip().lower())
    df["start_s"] = df["start"].apply(lambda x: time2s(x))
    df["end_s"] = df["end"].apply(lambda x: time2s(x))
    df["duration"] = df["end_s"] - df["start_s"]
    df.sort_values(["movie", "start_s", "end_s"], inplace=True)
    df["start_to_end"] = df["start_s"] - df["end_s"].shift(1)
    df["end_to_end"] = df["end_s"] - df["end_s"].shift(1)
    df.fillna(0, inplace=True)
    df = df.round(5)

    # fix
    to_be_fixed = [df[df["movie"] == x].index[0] for x in list(set(df["movie"].to_list()))]
    for x in to_be_fixed:
        df.loc[x, "start_to_end"] = 1000.0
        df.loc[x, "end_to_end"] = 1000.0

    # remove repeated
    df = df[(~df['movie'].str.contains('1001')) & (~df['movie'].str.contains('1010'))]

    df['sentence_someone'] = df['sentence'].apply(lambda x: rm_id(x))
    df['sentence_id'] = df['sentence'].apply(lambda x: rm_someone(x))

    df_meta = pd.read_csv(path_meta, names=['movie', 'link', 'category', 'color'], sep='\t')
    df_meta['category'] = df_meta['category'].str.lower()
    df_meta['movie_name'] = df_meta['movie'].str.replace('-', ' ').str.replace('_', '').str.lower().str.strip()
    df_meta = df_meta[['movie_name', 'category']]

    assert df.merge(df_meta, on='movie_name').shape[0] == df.shape[0]
    df = df.merge(df_meta, on='movie_name')

    df = df[
        ["movie", "movie_name", "clip", "category", "start_s", "end_s", "start_to_end", "end_to_end",
         "duration", "start_aligned", "end_aligned", "sentence", "sentence_someone", "sentence_id"]]

    df.reset_index(drop=True, inplace=True)
    df.to_csv(out_df, index=False, sep='\t')


def load_lsmdc_df(path_df):
    return pd.read_csv(path_df, encoding="ISO-8859-1", sep='\t')


def to_movie_name(movie):
    """
    convert original LSMDC movie name to readable movie name
    for example, 0001_American_Beauty -> american beauty
    :param movie:
    :return:
    """
    return movie.replace('_', ' ').replace('-', ' ').lower()


def indexing_lsmdc(out_json, path_frames):
    """
    index the LSMDC dataset as json file
    :param out_json: the output json file
    :param path_frames: the path of the frames root folder
    :return:
    """
    movies = sorted(list(path_frames.glob('*')), key=natural_keys_obj)

    clips = [list(m.glob('*')) for m in movies]

    frame_nb = [[len(list(c.glob('*.jpg'))) for c in c_lst] for c_lst in clips]

    # index to names
    i2n = {str(i_m): [m.name, {str(i_c): c.name for i_c, c in enumerate(clips[i_m])}] for i_m, m in enumerate(movies)}
    # names to index
    n2i = {m.name: [str(i_m), {c.name: str(i_c) for i_c, c in enumerate(clips[i_m])}] for i_m, m in enumerate(movies)}
    data = {i_m: {c: frame_nb[int(i_m)][int(c)] for c in i2n[i_m][1]} for i_m in i2n.keys()}

    json_dump(out_json, {
        'data': data,
        'i2n': i2n,
        'n2i': n2i
    }, formatting=False)


def lsmdc_dict(lsmdc):
    """
    Get the LSMDC frame entire structure as a dictionary
    {
    'i2n': {'0': ['0001_American_Beauty', {'0': 'clip_0', '1': 'clip_1', ...}]},
    'n2i': {'0001_American_Beauty': ['0', {'clip_0': '0', 'clip_1': '1', ...}]},
    'data': {'0': {'0': (number of clips), '1': (number of clips), ...}}
    }
    To save space, using i2n for "index to name", use n2i for "name to index"
    :param lsmdc: the loaded LSMDC json file
    :return:
    """
    i2n = lsmdc['i2n']
    d = lsmdc['data']
    d_ = {i2n[m][0]: {
        i2n[m][1][c]:
            list(range(d[m][c]))
        for c in d[m]
    } for m in d}
    return d_


def get_clips(movie, lsmdc):
    """
    Get the clips of a movie
    :param movie: the movie name
    :param lsmdc: the loaded LSMDC json file
    :return:
    """
    clips = sorted(lsmdc['n2i'][movie][1].keys())
    return clips


def mc2i(m, c, lsmdc):
    """
    Get the "id" of a movie clip. The "id" is used in a dataset json file

    :param m: movie name
    :param c: clip name
    :param lsmdc: the loaded LSMDC json file
    :return: the "id" of a movie clip
    """
    ref = lsmdc['n2i'][m]
    i = 'l_{}_{}'.format(ref[0], ref[1][c])
    return i


def mcf2i(m, c, f):
    """
    Get the "id" of a movie clip frame. The "id" is used in a dataset json file
    :param m: movie name
    :param c: clip name
    :param f: frame index
    :return: the "id" of a movie clip frame
    """
    ref = lsmdc['n2i'][m]
    i = 'l_{}_{}_{}'.format(ref[0], ref[1][c], f)
    return i


def i2mcf(i):
    """
    "id" to names of movie, clip, frame
    :param i: the "id" of a movie clip frame
    :return: movie name, clip name, frame index
    """
    _, i_m, i_c, i_f = i.split("_")
    ref = lsmdc["i2n"][i_m]
    m = ref[0]
    c = ref[1][i_c]
    return m, c, i_f


def i2mc(i):
    """
    "id" to names of movie, clip
    :param i: the "id" of a movie clip
    :return: movie name, clip name
    """
    _, i_m, i_c = i.split("_")
    ref = lsmdc["i2n"][i_m]
    m = ref[0]
    c = ref[1][i_c]
    return m, c


if __name__ == '__main__':
    path_base = Path(__file__).resolve().parent
    path_data = path_base / "data"
    path_lsmdc = path_data / "lsmdc.json"

    lsmdc = json.load(path_lsmdc.open('r'))
    data = lsmdc_dict()
