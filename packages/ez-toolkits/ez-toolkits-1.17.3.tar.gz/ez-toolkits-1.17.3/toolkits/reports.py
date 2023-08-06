from tkinter.messagebox import NO

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

    def generic(
        self, pieces=None,
        hosts=None, time_from=None, time_till=None, item_key=None, data_type=None,
        title=None, description=None,
        number_type=None, number_unit=None, number_handling=None,
        table_header_title=None, table_header_data=None, sort_by_ip=None,
        image_cid=None, image_label=None, image_kind=None
    ):

        _history = utils.retry(10, self._zbx.get_history_by_item_key, hosts, time_from, time_till, item_key, data_type)

        if _history != None:

            _files_func = self._files.multiple_pieces

            if pieces == 'single':

                _files_func = self._files.single_piece

                for _data in _history:
                    if len(_data['history']) > 0:
                        _history_last = max(_data['history'], key=lambda i: i['clock'])
                        _data['history'] = _history_last

            _image = {
                'cid': '{}'.format(image_cid),
                'path': '{}/{}_{}.png'.format(self._image_dir, self._image_name_prefix, image_cid),
                'label': image_label,
                'kind': image_kind
            }

            _files_result = _files_func(
                title=title,
                description=description,
                data=_history,
                image=_image,
                number_type=number_type,
                number_unit=number_unit,
                number_handling=number_handling,
                table_header_title=table_header_title,
                table_header_data=table_header_data,
                sort_by_ip=sort_by_ip
            )

            if _files_result == True:
                return _image
            else:
                return None

        else:

            return None

    def system_interface(self, hosts, interfaces, time_from, time_till, direction='in'):
        ''' System Interface '''

        _direction_name = 'Received'
        _direction_alias = 'received'
        _direction_info = '接收数据'

        if direction == 'out':
            _direction_name = 'Sent'
            _direction_alias = 'sent'
            _direction_info = '发送数据'

        _history = utils.retry(10, self._zbx.get_history_by_interface, hosts, interfaces, time_from, time_till, direction)

        if type(_history) == list and _history != []:

            _image = {
                'cid': 'system_interface_'.format(_direction_alias),
                'path': '{}/{}_system_interface_{}.png'.format(self._image_dir, self._image_name_prefix, _direction_alias)
            }

            _ = self._files.multiple_pieces(
                title='System Interface {}'.format(_direction_name),
                description='说明: 网卡**{}**的速度'.format(_direction_info),
                data=_history,
                image=_image,
                number_type='int',
                number_unit='Kbps',
                number_handling=utils.divisor_1000,
                sort_by_ip=True
            )

            if _ == True:
                return _image
            else:
                return None

        else:

            return None
