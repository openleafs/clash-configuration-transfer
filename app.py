import os
import re
import logging

import yaml
from flask import Flask, request, Response

from src.sub_link_transfer import SubLinkTransfer
from src.utils import get_config, get_file_from_r2, replace_name_for_proxy_group

app = Flask(__name__)

logging.basicConfig(filename=os.getcwd() + "/log/clash_configuration_transfer.log", level=logging.DEBUG,
                    format=f"%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s")

config = get_config()
SUB_LINK = config["proxy_link"]["sub_link"]
CUSTOM_LINK = config["proxy_link"]["custom_link"]
ACCESS_KEY = config["r2"]["access_key"]
SECRET_KEY = config["r2"]["secret_key"]


@app.route("/transfer", methods=["GET"])
def transfer():
    try:
        log_data = {
            "method": request.method,
            "path": request.path,
            "args": request.args,
            "data": request.data.decode("utf-8")
        }

        is_pass_link = request.args.get("is_pass_link")

        if is_pass_link is None:
            raise ValueError("You must offer a parameter")

        if int(is_pass_link) == 1:
            sub_link = SUB_LINK
            custom_link = CUSTOM_LINK
        else:
            sub_link = request.args.get("sub_link")
            custom_link = request.args.get("custom_link")

            if sub_link is None:
                raise ValueError("You must offer at least a sub link")

        app.logger.info(log_data)

        sub_link_transfer = SubLinkTransfer(sub_link, custom_link)
        proxies = sub_link_transfer.get_proxies_result()

        clash_file = get_file_from_r2("clash.yaml", ACCESS_KEY, SECRET_KEY)
        clash_configuration_template = yaml.safe_load(clash_file)
        clash_configuration_template["proxies"] = proxies

        clash_configuration = replace_name_for_proxy_group(clash_configuration_template)

        yaml_data = yaml.dump(clash_configuration, allow_unicode=True)
        response = Response(yaml_data, content_type="text/plain; charset=utf-8")

        return response
    except Exception as e:
        app.logger.error(e)
        return str(e)


@app.route("/rocket", methods=["GET"])
def shadow_rocket():
    try:
        log_data = {
            "method": request.method,
            "path": request.path,
            "args": request.args,
            "data": request.data.decode("utf-8")
        }

        app.logger.info(log_data)

        shadow_rocket_configuration = get_file_from_r2("shadowrocket.conf", ACCESS_KEY, SECRET_KEY)
        response = Response(shadow_rocket_configuration, content_type="text/plain; charset=utf-8")

        return response
    except Exception as e:
        app.logger.error(e)
        return str(e)


@app.route("/allow", methods=["GET"])
def allow_list():
    try:
        log_data = {
            "method": request.method,
            "path": request.path,
            "args": request.args,
            "data": request.data.decode("utf-8")
        }

        app.logger.info(log_data)

        sub_link_transfer = SubLinkTransfer(SUB_LINK)
        proxies = sub_link_transfer.get_proxies_result()

        allow_directives = [f"""allow {proxy["server"]};""" for proxy in proxies]

        # Write the directives to a file
        with open("resource/allowed-ips.conf", "w") as file:
            for directive in allow_directives:
                file.write(directive + "\n")

            hide_allow_directives = [re.sub(r"\d+.", "*.", i, 2) for i in allow_directives]
            return f"Update allow list successfully. IP list: {hide_allow_directives}"

    except Exception as e:
        app.logger.error(e)
        return str(e)


@app.route("/diff", methods=["GET"])
def diff_ip():
    try:
        log_data = {
            "method": request.method,
            "path": request.path,
            "args": request.args,
            "data": request.data.decode("utf-8")
        }

        app.logger.info(log_data)

        sub_link_transfer = SubLinkTransfer(SUB_LINK)
        proxies = sub_link_transfer.get_proxies_result()

        new_ip_address = [proxy["server"] for proxy in proxies]

        with open("resource/allowed-ips.conf", "r") as file:
            old_ip_address = [re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", line)[0] for line in file.readlines()]

            if new_ip_address == old_ip_address:
                return f"ip address does not changed"
            else:
                return f"ip address have changed"

    except Exception as e:
        app.logger.error(e)
        return str(e)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
