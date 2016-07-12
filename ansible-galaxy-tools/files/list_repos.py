#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
USAGE: python list_repos.py  --url_galaxy_ref <url galaxy reference> --url_galaxy_target <url galaxy target>
--adminkey_galaxy_target <glaxy target admin api key> --url_toolshed <url toolshed with tools>
--output_yaml <yaml output file>
'''
from bioblend.toolshed import ToolShedInstance
from bioblend.galaxy import GalaxyInstance
import yaml
import argparse


def toolshed_to_dict(options):
    ts = ToolShedInstance(url=options.url_toolshed)
    ts.verify = False
    repositories = ts.repositories.get_repositories()

    listrepos = []

    for repo in repositories:
        listrepos.append({'name': repo['name'], 'owner': repo['owner'], 'tool_panel_section_id': '',
                          'revisions': ts.repositories.get_ordered_installable_revisions(repo['name'], repo['owner'])})
    listrepos = set_section_id(ts, listrepos, options.url_galaxy_ref)
    dict_repos = {'api_key': options.adminkey_galaxy_target, 'galaxy_instance': options.url_galaxy_target, 'tools': listrepos}
    write_yaml(dict_repos, options.output_yaml)

def return_panel(guid, reftools):
    for reftool in reftools:
        if reftool['id'] == guid:
            return reftool['panel_section_id']

def set_section_id(ts, repos, url_galaxy_ref):
    gi = GalaxyInstance(url_galaxy_ref)
    gi.verify = False
    tools = gi.tools.get_tools()
    for repo in repos:
        for revision in repo['revisions']:
            if not repo['tool_panel_section_id']:
                revision_info = ts.repositories.get_repository_revision_install_info(repo['name'], repo['owner'], revision)
                for tool in revision_info[1]['valid_tools']:
                    panel_id = return_panel(tool['guid'], tools)
                    if panel_id:
                        repo['tool_panel_section_id'] = panel_id
    return repos


def write_yaml(repositories, yamlfile):
    with open(yamlfile, 'w') as outfile:
        outfile.write( yaml.safe_dump(repositories, encoding='utf-8', allow_unicode=True) )


if __name__ == "__main__":
    # Arguments parser
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--url_galaxy_ref', help='')
    parser.add_argument('--url_galaxy_target', help='')
    parser.add_argument('--adminkey_galaxy_target', help='')
    parser.add_argument('--url_toolshed', help='')
    parser.add_argument('--output_yaml', help='')
    args = parser.parse_args()
    toolshed_to_dict(args)

