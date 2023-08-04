import base64
import traceback

import requests
import yaml


class SubLinkTransfer:

    def __init__(self, sub_link: str, custom_link: str):
        self.sub_link = base64.b64decode(sub_link.encode("utf-8") + b"==").decode("utf-8")
        self.custom_link = base64.b64decode(custom_link.encode("utf-8") + b"==").decode("utf-8").split("|")

    @staticmethod
    def decode_base64_for_proxy_link(proxy_link: str):
        proxy_protocol, proxy_content = proxy_link.split("://")

        if proxy_protocol == "ss":
            proxy_configuration_base64, domain = proxy_content.split("#")
        else:
            proxy_configuration_base64 = proxy_content
            domain = ""

        proxy_configuration_byte = proxy_configuration_base64.encode("utf-8")
        proxy_configuration = base64.b64decode(proxy_configuration_byte + b"==").decode("utf-8")

        return proxy_protocol, proxy_configuration, domain

    @staticmethod
    def get_components_of_configuration(proxy_protocol: str, proxy_configuration: str, domain: str) -> dict:

        if proxy_protocol == "ss":
            components = proxy_configuration.split("@")
            cipher, password = components[0].split(":")
            address, port = components[1].split(":")
            return dict(
                name=domain,
                type="ss",
                server=address,
                port=int(port),
                cipher=cipher,
                password=password,
                udp=True
            )
        elif proxy_protocol == "vmess":
            tmp_dict = eval(proxy_configuration)

            components = dict(type="vmess")
            components["name"] = tmp_dict["ps"]
            components["server"] = tmp_dict["add"]
            components["port"] = int(tmp_dict["port"])
            components["uuid"] = tmp_dict["id"]
            components["alterId"] = int(tmp_dict["aid"])
            components["cipher"] = tmp_dict["scy"] if "scy" in tmp_dict else "auto"
            components["udp"] = True
            components["tls"] = False if "tls" in tmp_dict and tmp_dict["tls"] == "none" else True
            components["skip-cert-verify"] = False
            components["network"] = tmp_dict["net"] if "net" in tmp_dict else "tcp"

            if "host" in tmp_dict and tmp_dict["host"] != "":
                components["servername"] = tmp_dict["host"]

            if components["network"] == "ws":
                components["ws-opts"] = dict(path=tmp_dict["path"])
                if "sni" in tmp_dict and tmp_dict["sni"] != "":
                    components["ws-opts"]["headers"] = dict(Host=tmp_dict["sni"])

            return components
        else:
            print(f"Can't recognize the proxy_protocol {proxy_protocol}")

    def get_proxies_components(self, proxy_links: list) -> list:

        proxies = []

        for proxy_link in proxy_links:
            proxy_protocol, proxy_configuration, domain = self.decode_base64_for_proxy_link(proxy_link)
            components = self.get_components_of_configuration(proxy_protocol, proxy_configuration, domain)
            proxies.append(components)

        return proxies

    @staticmethod
    def replace_name_for_proxy_group(clash_configuration: dict):

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

    def get_result(self, file_name: str = "self_clash.yaml"):

        try:
            r = requests.get(self.sub_link)
            proxy_link_str = base64.b64decode(r.text.encode("utf-8") + b"==").decode("utf-8")

            proxy_links = proxy_link_str.split("\n")

            if self.custom_link is not None:
                proxy_links.extend(self.custom_link)

            proxies = self.get_proxies_components(proxy_links)

            with open("template.yaml", "rt", encoding="utf-8") as file:
                clash_configuration_template = yaml.safe_load(file)
                clash_configuration_template["proxies"] = proxies

            self_clash_configuration = self.replace_name_for_proxy_group(clash_configuration_template)

            with open(file_name, "w", encoding="utf-8") as file:
                yaml.dump(self_clash_configuration, file, default_flow_style=False)

            return self_clash_configuration

        except Exception as e:
            traceback.print_exc()
            return str(e)
