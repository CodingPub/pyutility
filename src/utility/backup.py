#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from utility.common import Common
from utility.log import Log

__all__ = ['backup']


def should_ignore_hours(ignore_hours):
    if not ignore_hours or len(ignore_hours) != 2:
        return False

    time = datetime.datetime.now()
    hour = time.hour
    return hour >= ignore_hours[0] and hour <= ignore_hours[1]


def backup(src, dst_dir, retemtion_days, hours_last_day=None, ignore_hours=None):

    if hours_last_day is None:
        hours_last_day = 8

    if should_ignore_hours(ignore_hours):
        return

    name = Common.filename(src) + '_' + datetime.datetime.now().strftime('%Y%m%d%H' + Common.file_extension(src))
    dst = Common.join_paths(dst_dir, name)
    Log.debug('backup %s to %s' % (src, dst))
    Common.create_dir(dst_dir)

    cmd = 'rsync -aE --progress %s %s' % (src, dst)
    Common.system_cmd(cmd)

    # delete older backups
    arr = [x for x in Common.list_dir(dst_dir) if x != '.DS_Store']
    for x in arr:
        name = Common.filename(x)
        t = name.split('_')
        if t and len(t) > 1:
            dt = datetime.datetime.strptime(t[-1], '%Y%m%d%H')
            days = (datetime.datetime.now() - dt).days
            should_delete = False
            if days >= 1:
                if days in retemtion_days:
                    if dt.hour < 23:
                        should_delete = True
                else:
                    should_delete = True
            elif days == 0 and dt.hour < 23 and (datetime.datetime.now() - dt).seconds > hours_last_day * 60 * 60:
                should_delete = True
            if should_delete:
                file = Common.join_paths(dst_dir, x)
                Common.remove(file)


def backup_with_config(config_path):
    content = Common.read_file(config_path)
    arr = Common.str2json(content)
    if arr:
        for x in arr:
            backup(x.get('src'), x.get('dst_dir'), x.get('retemtion_days'), hours_last_day=x.get('hours_last_day'), ignore_hours=x.get('ignore_hours'))


if __name__ == '__main__':
    Common.set_debug(True)

    config_path = Common.join_paths(Common.get_cmd_dir(), '..', 'tests', 'backup_test.json')
    config_path = Common.abs_path(config_path)
    if Common.debug():
        for day in range(0, 18):
            for hour in range(0, 24):
                path = '/tmp/backup/backup_test_201902%02d%02d.json' % (25 - day, hour)
                Common.replace_file(config_path, path)

    backup_with_config(config_path)
