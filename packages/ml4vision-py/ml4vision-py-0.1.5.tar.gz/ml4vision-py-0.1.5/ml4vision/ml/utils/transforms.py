import albumentations as A
from albumentations.pytorch import ToTensorV2

def get_train_transform(config, task='detection'):
    transform_list = []
    
    if config.resize:
        transform_list.append(A.SmallestMaxSize(max_size=config.min_size))
    if config.random_crop:
        crop_size = config.crop_size
        min_size = crop_size - crop_size * 0.15
        max_size = crop_size + crop_size * 0.15
        transform_list.append(A.RandomSizedCrop([int(min_size),int(max_size)],config.crop_size,config.crop_size))
    if config.flip_horizontal:
        transform_list.append(A.HorizontalFlip(p=0.5))
    if config.flip_vertical:
        transform_list.append(A.VerticalFlip(p=0.5))
    if config.random_brightness_contrast:
        transform_list.append(A.RandomBrightnessContrast(p=0.5))
    
    transform_list.extend([
        A.PadIfNeeded(min_height=None, min_width=None, pad_height_divisor=32,pad_width_divisor=32),
        A.Normalize(),
        ToTensorV2(),
    ])

    if task == 'detection':
        transform = A.Compose(
            transform_list,
            bbox_params=A.BboxParams('pascal_voc', 
            label_fields=['category_ids'], 
            min_visibility=0.1)
        )
    else:
        transform = A.Compose(transform_list)

    return transform

def get_val_transform(config, task='detection'):
    
    transform_list = [
        A.SmallestMaxSize(max_size=config.min_size),
        A.PadIfNeeded(min_height=None, min_width=None, pad_height_divisor=32,pad_width_divisor=32),
        A.Normalize(),
        ToTensorV2(),
    ]

    if task == 'detection':
        transform = A.Compose(
            transform_list,
            bbox_params=A.BboxParams('pascal_voc', 
            label_fields=['category_ids'], 
            min_visibility=0.1)
        )
    else:
        transform = A.Compose(transform_list)

    return transform