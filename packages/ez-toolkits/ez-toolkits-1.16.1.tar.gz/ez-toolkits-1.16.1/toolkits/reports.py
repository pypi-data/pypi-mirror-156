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
        _history = utils.retry(30, self._zbx.get_history_by_item_key, hosts, time_from, time_till, 'system.cpu.util', 0)
        if _history != None:
            _image = {
                'cid': 'system_cpu_utilization',
                'path': '{}/{}_system_cpu_utilization.png'.format(self._image_dir, self._image_name_prefix)
            }
            self._files.multiple_pieces(
                title='System CPU utilization',
                description='说明: 系统 CPU 使用率',
                data=_history,
                image=_image,
                number_type='float',
                number_unit='%',
                sort_by_ip=True
            )
            return _image
        else:
            return None

    def system_memory_utilization():
        # 内存
        item_history = utils.retry(30, zbx.get_history_by_item_key, hosts, time_from, time_till, 'vm.memory.utilization', 0)
        if item_history != None:
            image = {'cid': 'system_memory_utilization', 'path': '{}/{}_system_memory_utilization.png'.format(my_dir, image_filename_prefix)}
            images.append(image)
            my_files.multiple_pieces(
                title='System Memory utilization',
                description='说明: 系统内存使用率',
                data=item_history,
                image=image,
                number_type='float',
                number_unit='%',
                sort_by_ip=True
            )

    def system_root_partition_utilization():
        # 硬盘
        item_history = utils.retry(30, zbx.get_history_by_item_key, hosts, time_from, time_till, 'vfs.fs.size[/,pused]', 0)
        if item_history != None:
            for d in item_history:
                if len(d['history']) > 0:
                    history_last = max(d['history'], key=lambda i: i['clock'])
                    d['history'] = history_last
            image = {
                'cid': 'system_space_utilization_root',
                'path': '{}/{}_system_space_utilization_root.png'.format(my_dir, image_filename_prefix),
                'label': 'Used (%)',
                'kind': 'barh'
            }
            images.append(image)
            my_files.single_piece(
                title='System Space utilization (/)',
                description='说明: 系统硬盘分区使用率: /',
                data=item_history,
                image=image,
                number_type='float',
                number_unit='%',
                sort_by_ip=True
            )

    def system_interface_received():
        net_if_in = zbx.get_history_by_interface(hosts, hosts_interfaces, time_from, time_till, 'in')

        if type(net_if_in) == list and net_if_in != []:
            image = {'cid': 'interface_received', 'path': '{}/{}_interface_received.png'.format(my_dir, image_filename_prefix)}
            images.append(image)
            my_files.multiple_pieces(
                title='Interface Received',
                description='说明: 网卡**接收数据**的速度',
                data=net_if_in,
                image=image,
                number_type='int',
                number_unit='Kbps',
                number_handling=utils.divisor_1000,
                sort_by_ip=True
            )

    def system_interface_sent():
        net_if_out = zbx.get_history_by_interface(hosts, hosts_interfaces, time_from, time_till, 'out')

        if type(net_if_out) == list and net_if_out != []:
            image = {'cid': 'interface_sent', 'path': '{}/{}_interface_sent.png'.format(my_dir, image_filename_prefix)}
            images.append(image)
            my_files.multiple_pieces(
                title='Interface Sent',
                description='说明: 网卡**发送数据**的速度',
                data=net_if_out,
                image=image,
                number_type='int',
                number_unit='Kbps',
                number_handling=utils.divisor_1000,
                sort_by_ip=True
            )
