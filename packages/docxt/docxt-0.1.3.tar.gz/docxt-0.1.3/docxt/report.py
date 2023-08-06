# -*- encoding: utf-8 -*-
'''
Filename         :report.py
Description      :
Time             :2021/09/26 17:22:09
Author           :***
Email            :barwechin@163.com
'''

import subprocess
from typing import Sequence
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm

REPLACE_NONE_WITH = '无'


def check_data(tpl: DocxTemplate, data: dict):
    """
    Check data to render the template and make some convertions automatically.

    Parameters:
    - `tpl` - a DocxTemplate instance provided by docxtpl
    - `data` - a dict with all literal values. Some special values such as image paths
    will be converted to proper image objects according to the configuration provided.

    Returns: a `dict` instance, checked data after some convertions.
    """

    def image_object(options: dict):
        """
        Convert image path to image object using `InlineImage` provided by docx.

        Parameters:
        - `options` - a dict. `path` is a necessary term, `width` and `height` is options.

        Returns: an `InlineImage` instance.
        """
        if not isinstance(options, dict):
            raise TypeError('Options must be a dict instance.')
        img_path = options.get('path', None)
        if img_path is None:
            raise ValueError('Image path cannot be null.')
        img_width = options.get('width', 140)
        img_height = options.get('height', None)
        img_height = None if img_height is None else Mm(img_height)
        return InlineImage(tpl, img_path, Mm(img_width), img_height)

    def convert(d):
        """
        Iterate, check and convert each term of provided data recursively.

        Parameters:
        - `d` - a dict.

        Returns: a part-converted data.
        """
        for k, v in d.items():
            if k == 'img':
                options = {'path': v} if isinstance(v, str) else v
                d['img'] = image_object(options)
            elif isinstance(v, dict):
                # 值为字典时进行递归检查
                d[k] = convert(v)
            elif isinstance(v, list):
                # 图片数组：路径转换为对象。要求数组每个元素都是一个图片配置
                # 即包含path属性，同时其type属性为'image'。
                if len(v) > 0 and isinstance(v[0], dict) and 'type' in v[0].keys() and v[0]['type'] == 'image':
                    d[k] = [image_object(item) for item in v]
            elif v is None:
                d[k] = REPLACE_NONE_WITH
        return d

    return convert(data)


def generateReport(template: str, data: dict, output_filepath: str):
    """
    Generate a report from a specified template, both are .docx files.

    Parameters:
    - `template` - a docx file as template
    - `data` - a dict to render the template. An image can be provided as a path
    string or as a configuration dict which include necessary attributes `path`
    and some optional attributes such as `width` and `height`. A sequence of images
    can only be provided as a series of configuration dicts to be distinguished from
    regular sequences. In this case, image configuration must have attribute `type` and
    its value is `"image"`. Other options are likely to the first case we refered.
    - `output_filepath` - where to save the rendered docx report
    """
    docx = DocxTemplate(template)
    checked_data = check_data(docx, data)
    docx.render(checked_data)
    docx.save(output_filepath)


def packageAttachments(targets: Sequence[str], dest: str):
    """
    Package and zip specified files into one zipped file.
    """
    p = subprocess.Popen(f"tar -zcf {dest} {' '.join(targets)}", shell=True, stdout=subprocess.PIPE)
    std_out = p.stdout.readlines() if p.stdout else None
    std_err = p.stderr.readlines() if p.stderr else None
    return [std_out, std_err]
