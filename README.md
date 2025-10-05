# Sc2St Dataset Preparation

This is the dataset for the paper **Script-to-Storyboard: A New Contextual Retrieval Dataset and Benchmark**

## Step 1 - Prepare LSMDC dataset
1. You need first request access to the dataset from [Large Scale Movie Description Challenge (LSMDC)](https://sites.google.com/site/describingmovies/download)
2. Download the video and annotation files using the following steps:
   1. Download the [video downloading scripts](https://datasets.d2.mpi-inf.mpg.de/movieDescription/protected/lsmdc2016/downloadChallengeData.sh) to `LSMDC` folder
   2. Switch to `LSMDC` folder using `cd LSMDC`
   3. run with `bash downloadChallengeData.sh <username-MPIIMD> <password-MPIIMD>` where `<username-MPIIMD>` and `<password-MPIIMD>` are the username and password you used to request access to the dataset
3. Run `python main.py` to extract the frames from movie clips

## Step 2 - Use the Sc2St dataset
Download the Sc2St dataset in [Google Drive](https://drive.google.com/drive/folders/1NMlZpLoHsRfI2Iz9eeJ23w27zihi9zSR?usp=sharing)
The dataset structure is as follows:
```
Sc2St
├── story10_all
│   ├── story10_all.json
│   ├── story10_all_val.json
│   ├── story10_all_test.json
│   ├── story10_all_train.json
│   ├── story10_all_trainval.json
│   ├── story10_all_train_no.json
│   ├── ...
│   ├── story10_all_val_no.json
├── i2chars.json
│── parsed_clip.json
│── parsed_text.json
```
The `story10_all` indicates the dataset is for storyboard with 10 images in a `story`, where `all` means it uses all the movies.
### Movie, Clip or Frame Id
The `.json` files contains `id` that is a unique identifier for each movie clip frame in the format `l_1_2_1`, which `l` means LSMDC, and the three numbers are `movie_id`, `clip_id`, and `frame_id` respectively.
The parsing code can be found in `lsmdc_utils.py`.
If the id has only 2 digits, it represents the `movie_id` and `clip_id` respectively, for example, `l_1_2` means the movie with id `1` and the clip with id `2`.
### Data split
The json file ending with `train` or `val` or `test` indicates the data split for training, validation, and testing respectively.
### Overlapping
The json file ending with `_no` indicates there is no overlapping of used frames across splits `train`, `val`, and `test`.

### Other information
These raw information are used in building the dataset, provided here for reference.
- `i2chars.json` contains the mapping from the `clip id` to characters in that frame.
- `parsed_clip.json` contains the mapping of `clip id` to its parsed keyframes indices.
- `parsed_text.json` contains the mapping of `clip id` to its parsed text. A clip may have multiple text descriptions.

## About this repo
- `data` folder contains intermediate prepared data for LSMDC dataset.
  - `lsmdc.json` is the indexed LSMDC dataset frame directory structure, containing id for all movies, clips, and frames. Use this file together with `lsmdc_utils.py` to parse the id.
  - `meta.csv` is the metadata for LSMDC dataset, containing information including movie genres.
- `lsmdc_utils.py` contains the parsing code for LSMDC dataset.
- `main.py` contains the code for extracting frames from movie clips.
- `utils.py` contains utility functions.
