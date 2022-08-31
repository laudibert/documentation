#!/usr/bin/env python3
import glob
import json
import os
import yaml
from itertools import chain
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

TEMPLATE = """\
---
{front_matter}
---

{content}
"""

def catalog(content, content_dir):
    logger.info("Starting Catalog action...")
    print(content)
    for file_name in chain.from_iterable(glob.glob(pattern, recursive=True) for pattern in content["globs"]):
        # print(file_name)
        bundle_excludes = content["options"].get('bundle_excludes', [])
        if any(substring in file_name for substring in bundle_excludes) or file_name.endswith('manifest.schema.json'):
            logging.info(f"skipping {file_name}")
        else:
            logging.info(f"Processing {file_name}")
            if file_name.endswith(".json"):
                with open(file_name, mode="r+") as f:
                    try:
                        data = json.loads(f.read())
                    except:
                        logger.warn(f"Error parsing {file_name}")
            if data:
                p = Path(file_name)
                for action_name, action_data in data.get('actions', {}).items():
                    output_file_name = data.get('name')\
                        .replace('com.datadoghq.dd.','')\
                        .replace('com.datadoghq.','')\
                        .replace('.', '_')
                    action_data['bundle'] = data.get('name')
                    action_data['bundle_title'] = data.get('title').strip()
                    action_data['source'] = data.get('icon', {}).get('integration_id', '')
                    # if this is a dd. bundle then lets use the datadog integration id
                    if not action_data['source'] and 'datadog' in action_data['bundle_title'].lower():
                        action_data['source'] = '_datadog'
                    output_content = TEMPLATE.format(front_matter=yaml.dump(action_data, default_flow_style=False).strip(), content=action_data.get('description'))
                    dest_dir = Path(f"{content_dir}/catalog/")
                    dest_dir.mkdir(exist_ok=True)
                    name = f"{output_file_name}_{action_name}"
                    dest_file = dest_dir.joinpath(name).with_suffix('.md')
                    print(dest_file)
                    with open(dest_file, mode='w', encoding='utf-8') as out_file:
                        out_file.write(output_content)
