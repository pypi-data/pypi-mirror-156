import os.path
import asyncio
import aiohttp
from docparser.core.behavior_base import BehaviorBase
from docparser.core.tools import Tools


class TextRepairBehavior(BehaviorBase):
    class_index = 0

    def data_processing(self, ref_data, data: list, error: list, config: dict, logger, additional) -> dict:

        conf = config.get("text_repair")

        if 'file' not in additional or conf is None:
            return additional

        sub_conf = conf.get('subs')

        if sub_conf is None:
            return additional

        sub_conf = [Tools.init_regex(item) for item in sub_conf]

        lines = asyncio.run(self.__convert(additional, conf))

        if lines:

            if lines and isinstance(lines, list):
                for line in lines:
                    for sub in sub_conf:
                        res = Tools.match_value(line, sub)
                        if res is not None and isinstance(res, dict):
                            for k, v in res.items():
                                data[k] = v
                                if k == conf.get('stop'):
                                    return additional

        return additional

    async def __convert(self, additional, conf):

        file = additional.get('file')
        file_suffix = os.path.splitext(file)
        if file_suffix[1].lower() != '.xlsx':
            return None
        pdf_url = conf.get("pdf_api")
        url_params = {"filepath": f'{file_suffix[0]}.pdf', "doctype": 'txt'}
        header = {
            "Content-type": "application/json"
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(pdf_url, headers=header, json=url_params) as res:
                    if res.ok:
                        res_content = await res.json(content_type=None)
                        if res_content.get("status"):
                            return res_content.get("data")
        except Exception:
            pass
