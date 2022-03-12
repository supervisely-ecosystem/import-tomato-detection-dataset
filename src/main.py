
import os, random, zipfile
import supervisely as sly
from bs4 import BeautifulSoup
from supervisely.io.fs import get_file_name
import sly_globals as g
import gdown


def create_ann(ann_path):
    labels = []

    with open(ann_path, 'r') as f:
        data = f.read()

    bs_data = BeautifulSoup(data)
    width = int(bs_data.find(g.width_field).text)
    height = int(bs_data.find(g.height_field).text)
    for coord_data in bs_data.find_all(g.coord_field):
        left, top, right, bottom = coord_data.text[1:-1].split('\n')
        rectangle = sly.Rectangle(int(top), int(left), int(bottom), int(right))
        label = sly.Label(rectangle, g.obj_class)
        labels.append(label)

    return sly.Annotation(img_size=(height, width), labels=labels)


def extract_zip():
    if zipfile.is_zipfile(g.archive_path):
        with zipfile.ZipFile(g.archive_path, 'r') as archive:
            archive.extractall(g.work_dir_path)
    else:
        g.logger.warn('Archive cannot be unpacked {}'.format(g.arch_name))
        g.my_app.stop()


@g.my_app.callback("import_tomato_detection")
@sly.timeit
def import_tomato_detection(api: sly.Api, task_id, context, state, app_logger):

    gdown.download(g.tomato_url, g.archive_path, quiet=False)
    extract_zip()

    images_path = os.path.join(g.work_dir_path, g.images_folder)
    anns_path = os.path.join(g.work_dir_path, g.anns_folder)

    new_project = api.project.create(g.WORKSPACE_ID, g.project_name, change_name_if_conflict=True)
    api.project.update_meta(new_project.id, g.meta.to_json())

    new_dataset = api.dataset.create(new_project.id, g.dataset_name, change_name_if_conflict=True)

    sample_img_names = random.sample(os.listdir(images_path), g.sample_img_count)

    progress = sly.Progress('Upload items', len(sample_img_names), app_logger)
    for img_batch in sly.batched(sample_img_names, batch_size=g.batch_size):

        img_pathes = [os.path.join(images_path, name) for name in img_batch]
        img_infos = api.image.upload_paths(new_dataset.id, img_batch, img_pathes)
        img_ids = [im_info.id for im_info in img_infos]
        ann_pathes = [os.path.join(anns_path, get_file_name(name) + '.xml') for name in img_batch]

        anns = [create_ann(ann_path) for ann_path in ann_pathes]
        api.annotation.upload_anns(img_ids, anns)

        progress.iters_done_report(len(img_batch))

    g.my_app.stop()


def main():
    sly.logger.info("Script arguments", extra={
        "TEAM_ID": g.TEAM_ID,
        "WORKSPACE_ID": g.WORKSPACE_ID
    })
    g.my_app.run(initial_events=[{"command": "import_tomato_detection"}])


if __name__ == '__main__':
    sly.main_wrapper("main", main)