from flask import Response, request
from io import BytesIO
import xml.etree.ElementTree

from fHDHR.tools import channel_sort, sub_el


class Lineup_XML():
    endpoints = ["/lineup.xml", "/hdhr/lineup.xml"]
    endpoint_name = "hdhr_lineup_xml"

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

    def __call__(self, *args):
        return self.get(*args)

    def get(self, *args):

        base_url = request.url_root[:-1]

        show = request.args.get('show', default="all", type=str)

        channelslist = {}
        for fhdhr_id in [x["id"] for x in self.fhdhr.device.channels.get_channels()]:
            channel_obj = self.fhdhr.device.channels.list[fhdhr_id]
            if channel_obj.enabled or show == "found":
                lineup_dict = channel_obj.lineup_dict
                lineup_dict["URL"] = "%s%s" % (base_url, lineup_dict["URL"])
                if show == "found" and channel_obj.enabled:
                    lineup_dict["Enabled"] = 1
                elif show == "found" and not channel_obj.enabled:
                    lineup_dict["Enabled"] = 0

            channelslist[channel_obj.number] = lineup_dict

        # Sort the channels
        sorted_channel_list = channel_sort(list(channelslist.keys()))
        sorted_chan_guide = []
        for channel in sorted_channel_list:
            sorted_chan_guide.append(channelslist[channel])

        out = xml.etree.ElementTree.Element('Lineup')
        for lineup_dict in sorted_chan_guide:
            program_out = sub_el(out, 'Program')
            for key in list(lineup_dict.keys()):
                sub_el(program_out, str(key), str(lineup_dict[key]))

        fakefile = BytesIO()
        fakefile.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        fakefile.write(xml.etree.ElementTree.tostring(out, encoding='UTF-8'))
        lineup_xml = fakefile.getvalue()

        return Response(status=200,
                        response=lineup_xml,
                        mimetype='application/xml')
