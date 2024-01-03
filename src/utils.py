import os
import yaml
import base64
import configparser

import requests


script_path = os.path.abspath(__file__)
working_dir = os.path.dirname(script_path)


def get_config(config_name: str = "config.ini") -> configparser:
    config = configparser.ConfigParser()
    config.read(f"{working_dir}/{config_name}")
    return config


def decode_base64_str(base64_str: str) -> str:
    return base64.b64decode(base64_str.encode("utf-8") + b"==").decode("utf-8")


def get_file_from_r2(file_name: str, access_key: str, secret_key: str) -> bytes:
    url = f"https://config-template.leafsyang.com/{file_name}"
    headers = {
        "X-ACCESS-KEY": access_key,
        "X-SECRET-KEY": secret_key
    }

    r = requests.get(url=url, headers=headers)
    return r.content


def replace_name_for_proxy_group(clash_configuration: dict) -> dict:

    proxies = clash_configuration["proxies"]
    jms_names = [item["name"] for item in proxies if "JMS" in item["name"]]

    new_proxy_groups = []
    for proxy_group in clash_configuration["proxy-groups"]:
        tmp_proxy_group = proxy_group.copy()

        proxies_str_in_proxy_group = ",".join(proxy_group["proxies"])

        if "JMS" in proxies_str_in_proxy_group:
            no_jms_proxies = filter(lambda x: x if "JMS" not in x else None, proxy_group["proxies"])

            new_jms_proxies = list(no_jms_proxies)
            new_jms_proxies.extend(jms_names)
            tmp_proxy_group["proxies"] = new_jms_proxies

            new_proxy_groups.append(tmp_proxy_group)
        else:
            new_proxy_groups.append(proxy_group)

    clash_configuration["proxy-groups"] = new_proxy_groups

    return clash_configuration