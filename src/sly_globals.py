
import os, sys
from pathlib import Path
import supervisely as sly
from collections import defaultdict


my_app = sly.AppService()
api: sly.Api = my_app.public_api

root_source_dir = str(Path(sys.argv[0]).parents[1])
sly.logger.info(f"Root source directory: {root_source_dir}")
sys.path.append(root_source_dir)

TASK_ID = int(os.environ["TASK_ID"])
TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])

logger = sly.logger

sample_percent = int(os.environ["modal.state.samplePercent"])
# sample_percent = 20 #TODO to debug
sample_img_count = round(6.43 * sample_percent)

project_name = 'tomato detection'
work_dir = 'tomato_data'
tomato_url = 'https://storage.googleapis.com/kaggle-data-sets/734964/1274935/bundle/archive.zip?X-Goog-Algorithm=GOOG4-' \
            'RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20220311%2Fauto%2' \
            'Fstorage%2Fgoog4_request&X-Goog-Date=20220311T163732Z&X-Goog-Expires=259199&X-Goog-SignedHeaders=host&X-' \
            'Goog-Signature=3401bec5b55918ed113e34c47bdef1bc6dd283570c79cb2131800d04b7643819674b4459727f56d1ae6704632e' \
            '10ba9211bb0ceb5de7649d1285e30e8f4a49351e93f2ea4d16f86608bd734c32e5a73cd33ea22507b2916a54ce95b0a7b5b0ba091c' \
            'c7a2ade8fdd80ab80876af1febefb8b3e6c3db374182073c0bd2d27c979516f651517bcf4c6235427ca2098de76838e1a1e2255c9a' \
            'd34b5d1d53386f97f829d6b1bf5b526fdb7f9085bace43067b7eb0b64e69d6e4c34c8b4156c4c00cbfb20d36576db7accba67daa30' \
            '934c11e4793c16fb48fe71f76e33db6b026670026a079fee91fd95acc90df6a82e56afa74c527f9348774884ff0576c33a9c7378'

arch_name = 'TomatoPascalVOC.zip'

images_folder = 'images'
anns_folder = 'annotations'
batch_size = 30
class_name = 'tomato'
dataset_name = 'ds'
coord_field = 'bndbox'
width_field = 'width'
height_field = 'height'

obj_class = sly.ObjClass(class_name, sly.Rectangle)
obj_class_collection = sly.ObjClassCollection([obj_class])

meta = sly.ProjectMeta(obj_classes=obj_class_collection)

storage_dir = my_app.data_dir
work_dir_path = os.path.join(storage_dir, work_dir)
sly.io.fs.mkdir(work_dir_path)
archive_path = os.path.join(work_dir_path, arch_name)
