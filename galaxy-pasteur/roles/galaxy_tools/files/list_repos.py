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
import pprint


def toolshed_to_dict(options):
    ts = ToolShedInstance(url=options.url_toolshed)
    ts.verify = False
    repositories = ts.repositories.get_repositories()

    listrepos = []

    for repo in repositories:
        revisions = ts.repositories.get_ordered_installable_revisions(repo['name'], repo['owner'])
        if len(revisions) > 0:
            revision = revisions[-1:]
        listrepos.append({'name': repo['name'], 'owner': repo['owner'], 'tool_panel_section_id': '', 'tool_shed_url': options.url_toolshed,
                          'tool_panel_section_label': '', 'revisions': revision, 'verify_ssl': False})
    listrepos = set_section_id(ts, listrepos, options.url_galaxy_ref)
    dict_repos = {'api_key': options.adminkey_galaxy_target, 'galaxy_instance': options.url_galaxy_target, 'tools': listrepos}
    write_yaml(dict_repos, options.output_yaml)

def return_panel(guid, reftools):
    for reftool in reftools:
        if reftool['id'] == guid:
            return [reftool['panel_section_id'], reftool['panel_section_name']]

def set_section_id(ts, repos, url_galaxy_ref):
    gi = GalaxyInstance(url_galaxy_ref)
    gi.verify = False
    tools = gi.tools.get_tools()
    clean_repos = []
    for repo in repos:
        for revision in repo['revisions']:
            if not repo['tool_panel_section_id']:
                revision_info = ts.repositories.get_repository_revision_install_info(repo['name'], repo['owner'], revision)
                if 'valid_tools' in revision_info[1]:
                    for tool in revision_info[1]['valid_tools']:
                        panel_info = return_panel(tool['guid'], tools)
                        if panel_info:
                            repo['tool_panel_section_id'] = panel_info[0]
                            repo['tool_panel_section_label'] = panel_info[1]
                            clean_repos.append(repo)
                            break
    return clean_repos


def write_yaml(repositories, yamlfile):
    pprint.pprint(repositories)
    with open(yamlfile, 'w') as outfile:
        outfile.write( yaml.safe_dump(repositories, encoding='utf-8', allow_unicode=True) )


if __name__ == "__main__":
    # Arguments parser
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--url_galaxy_ref', help='Reference Galaxy instance URL/IP address')
    parser.add_argument('--url_galaxy_target', help='Target Galaxy instance URL/IP address')
    parser.add_argument('--adminkey_galaxy_target', help='Galaxy admin user API key')
    parser.add_argument('--url_toolshed', help='The Tool Shed URL where to install the tool from')
    parser.add_argument('--output_yaml', help='tool list to install yaml file')
    args = parser.parse_args()
    toolshed_to_dict(args)


