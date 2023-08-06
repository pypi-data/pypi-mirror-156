from . import files, utils, zabbix

'''
reports.logout()

    生成报告完成以后, 退出 Zabbix

return _image

    返回图片信息, 发邮件时使用
'''

class reports(object):

    # Zabbix Instance
    _zbx = None

    # Files Instance
    _files = None

    # Image Object
    _image_dir = '.'
    _image_name_prefix = 'image'

    def __init__(self, zabbix_api_url, zabbix_username, zabbix_password, markdown_file, html_file, image_dir, image_name_prefix):
        ''' Initiation '''
        self._zbx = zabbix.api(zabbix_api_url, zabbix_username, zabbix_password)
        self._files = files.files(markdown_file, html_file)
        self._image_dir = image_dir
        self._image_name_prefix = image_name_prefix

    def logout(self):
        self._zbx.logout()

    def system_cpu_utilization(self, hosts, time_from, time_till):
        ''' System CPU utilization '''
        _history = utils.retry(10, self._zbx.get_history_by_item_key, hosts, time_from, time_till, 'system.cpu.util', 0)
        if _history != None:
            _image = {
                'cid': 'system_cpu_utilization',
                'path': '{}/{}_system_cpu_utilization.png'.format(self._image_dir, self._image_name_prefix)
            }
            self._files.multiple_pieces(
                title='System CPU utilization',
                description='说明: 系统CPU使用率',
                data=_history,
                image=_image,
                number_type='float',
                number_unit='%',
                sort_by_ip=True
            )
            return _image
        else:
            return None

    def system_memory_utilization(self, hosts, time_from, time_till):
        ''' System Memory utilization '''
        _history = utils.retry(10, self._zbx.get_history_by_item_key, hosts, time_from, time_till, 'vm.memory.utilization', 0)
        if _history != None:
            _image = {
                'cid': 'system_memory_utilization',
                'path': '{}/{}_system_memory_utilization.png'.format(self._image_dir, self._image_name_prefix)
            }
            self._files.multiple_pieces(
                title='System Memory utilization',
                description='说明: 系统内存使用率',
                data=_history,
                image=_image,
                number_type='float',
                number_unit='%',
                sort_by_ip=True
            )
            return _image
        else:
            return None

    def system_root_partition_utilization(self, hosts, time_from, time_till):
        ''' System root partition utilization '''
        _history = utils.retry(10, self._zbx.get_history_by_item_key, hosts, time_from, time_till, 'vfs.fs.size[/,pused]', 0)
        if _history != None:
            for _data in _history:
                if len(_data['history']) > 0:
                    _history_last = max(_data['history'], key=lambda i: i['clock'])
                    _data['history'] = _history_last
            _image = {
                'cid': 'system_root_partition_utilization',
                'path': '{}/{}_system_root_partition_utilization.png'.format(self._image_dir, self._image_name_prefix),
                'label': 'Used (%)',
                'kind': 'barh'
            }
            self._files.single_piece(
                title='System root partition utilization',
                description='说明: 系统 / 分区使用率',
                data=_history,
                image=_image,
                number_type='float',
                number_unit='%',
                sort_by_ip=True
            )
            return _image
        else:
            return None

    def system_interface_received(self, hosts, interfaces, time_from, time_till):
        ''' System Interface Received '''
        _net_if_in = utils.retry(10, self._zbx.get_history_by_interface, hosts, interfaces, time_from, time_till, 'in')
        if type(_net_if_in) == list and _net_if_in != []:
            _image = {
                'cid': 'system_interface_received',
                'path': '{}/{}_system_interface_received.png'.format(self._image_dir, self._image_name_prefix)
            }
            self._files.multiple_pieces(
                title='System Interface Received',
                description='说明: 网卡**接收数据**的速度',
                data=_net_if_in,
                image=_image,
                number_type='int',
                number_unit='Kbps',
                number_handling=utils.divisor_1000,
                sort_by_ip=True
            )
            return _image
        else:
            return None

    def system_interface_sent(self, hosts, interfaces, time_from, time_till):
        ''' System Interface Sent '''
        _net_if_out = utils.retry(10, self._zbx.get_history_by_interface, hosts, interfaces, time_from, time_till, 'out')
        if type(_net_if_out) == list and _net_if_out != []:
            _image = {
                'cid': 'system_interface_sent',
                'path': '{}/{}_system_interface_sent.png'.format(self._image_dir, self._image_name_prefix)
            }
            self._files.multiple_pieces(
                title='System Interface Sent',
                description='说明: 网卡**发送数据**的速度',
                data=_net_if_out,
                image=_image,
                number_type='int',
                number_unit='Kbps',
                number_handling=utils.divisor_1000,
                sort_by_ip=True
            )
            return _image
        else:
            return None

    def process_object(self, hosts, time_from, time_till, item_name, item_alias, proc_name, proc_user, proc_cmdline):

        # CPU utilization
        _item_key = 'proc.cpu.util[{},{},,{}]'.format(proc_name, proc_user, proc_cmdline)
        _history = utils.retry(10, self._zbx.get_history_by_item_key, hosts, time_from, time_till, _item_key, 0)
        if _history != None:
            _image = {
                'cid': '{}_cpu_utilization'.format(item_alias),
                'path': '{}/{}_{}_cpu_utilization.png'.format(self._image_dir, self._image_name_prefix, item_alias)
            }
            self._files.multiple_pieces(
                title='{} CPU utilization'.format(item_name),
                description='说明: {} CPU 使用率'.format(item_name),
                data=_history,
                image=_image,
                number_type='float',
                number_unit='%',
                sort_by_ip=True
            )

        # Memory used
        _item_key = 'proc.mem[{},{},,{},rss]'.format(proc_name, proc_user, proc_cmdline)
        _history = utils.retry(10, self._zbx.get_history_by_item_key, hosts, time_from, time_till, _item_key, 0)
        if _history != None:
            _image = {
                'cid': '{}_memory_usage_rss'.format(item_alias),
                'path': '{}/{}_{}_memory_usage_rss.png'.format(self._image_dir, self._image_name_prefix, item_alias)
            }
            self._files.multiple_pieces(
                title='{} Memory usage (rss)'.format(item_name),
                description='说明: {} 内存使用量'.format(item_name),
                data=_history,
                image=_image,
                number_type='int',
                number_unit='MB',
                number_handling=utils.divisor_square_1024,
                sort_by_ip=True
            )
