import os
import json

def upload_model(config, model_name=None):

    model_name = model_name or f"{config.project_info['name']}-model"
    annotation_type = "BBOX" if config.task == 'detection' else "SEGMENTATION"
    architecture = 'object_detection_fn' if annotation_type == "BBOX" else "segmentation_fn"

    model = config.client.get_or_create_model(
        model_name,
        description='',
        project = config.client.get_project_by_name(config.project_info['name'], config.project_info['owner']).uuid,
        categories=config.project_info['categories'],
        annotation_type=annotation_type,
        architecture=architecture
    )

    with open(os.path.join(config.save_location, 'metrics.json'), 'r') as f:
        metrics = json.load(f)

    print('adding version')
    if annotation_type == "BBOX":
            
        model.add_version(
            os.path.join(config.save_location, 'best_val_model.pt'),
            params = {
                'min_size': config.transform.min_size,
                'pad': 32,
                'normalize': True,
                'threshold': float(metrics["working_point"]["confidence"])
            },
            metrics = {
                'map': round(metrics["map"], 3),
                'precision': round(metrics["working_point"]["precision"], 3),
                'recall': round(metrics["working_point"]["recall"], 3)
            }
        )

    else:
        model.add_version(
            os.path.join(config.save_location, 'best_val_model.pt'),
            params = {
                'min_size': config.transform.min_size,
                'pad': 32,
                'normalize': True,
            },
            metrics = {
                'miou': round(metrics["mean_iou"], 3)
            }
        )

