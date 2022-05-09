
import pandas as pd
from os import listdir
from os.path import isfile, join
import os

path = os.path.dirname(os.path.realpath(__file__))
onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
file_names = [file_name for file_name in onlyfiles if file_name.endswith(".mp4")]
metadata = pd.read_csv("metadata.csv")
file_names = [sub.replace(".mp4", '') for sub in file_names]
file_names.sort(key=int)

print(len(metadata.index))
print(len(file_names))
# updating the column value/data
for index, file in enumerate(file_names):
	print("original metadata")
	print(metadata.iloc[index, metadata.columns.get_loc('video_id')])
	print("file_names")
	print(file_names[index])
	metadata.iloc[index, metadata.columns.get_loc('video_id')]  = file_names[index]
	print("new metadata")
	print(metadata.iloc[index, metadata.columns.get_loc('video_id')])
  
# writing into the file
metadata.to_csv("AllDetails.csv", index=False)
