import traceback

import requests

from src.utils import decode_base64_str


class SubLinkTransfer:

    def __init__(self, sub_link: str, custom_link: str = None):
        self.sub_link = decode_base64_str(sub_link)
        self.custom_link = None if custom_link is None else decode_base64_str(custom_link).split("|")

    @staticmethod
    def decode_base64_for_proxy_link(proxy_link: str) -> tuple[str, str, str]:
        proxy_protocol, proxy_content = proxy_link.split("://")

        if proxy_protocol == "ss":
            proxy_configuration_base64, domain = proxy_content.split("#")
        else:
            proxy_configuration_base64 = proxy_content
            domain = ""

        proxy_configuration = decode_base64_str(proxy_configuration_base64)

        return proxy_protocol, proxy_configuration, domain

    @staticmethod
    def transfer(proxy_protocol: str, proxy_configuration: str, domain: str) -> dict:

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
            raise ValueError(f"Can't recognize the proxy_protocol {proxy_protocol}")

    def get_proxies_components(self, proxy_links: list) -> list:

        proxies = []

        for proxy_link in proxy_links:
            proxy_protocol, proxy_configuration, domain = self.decode_base64_for_proxy_link(proxy_link)
            components = self.transfer(proxy_protocol, proxy_configuration, domain)
            proxies.append(components)

        return proxies

    def get_proxies_result(self) -> list:
        try:
            r = requests.get(self.sub_link)
            proxy_link_str = decode_base64_str(r.text)

            proxy_links = proxy_link_str.split("\n")

            if self.custom_link is not None:
                proxy_links.extend(self.custom_link)

            proxies = self.get_proxies_components(proxy_links)

            return proxies

        except Exception as e:
            traceback.print_exc()
            return [e]
