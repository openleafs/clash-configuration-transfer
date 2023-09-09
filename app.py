import os
import re
import logging
import configparser

import yaml
from flask import Flask, request, Response

from src.sub_link_transfer import SubLinkTransfer

app = Flask(__name__)

logging.basicConfig(filename=os.getcwd() + "/log/clash_configuration_transfer.log", level=logging.DEBUG,
                    format=f"%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s")


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
            config = configparser.ConfigParser()
            config.read("src/config.ini")
            sub_link = config["proxy_link"]["sub_link"]
            custom_link = config["proxy_link"]["custom_link"]
        else:
            sub_link = request.args.get("sub_link")
            custom_link = request.args.get("custom_link")

            if sub_link is None:
                raise ValueError("You must offer at least a sub link")

        app.logger.info(log_data)

        sub_link_transfer = SubLinkTransfer(sub_link, custom_link)
        clash_configuration = sub_link_transfer.get_result()

        yaml_data = yaml.dump(clash_configuration, allow_unicode=True)
        response = Response(yaml_data, content_type="text/plain; charset=utf-8")

        return response
    except Exception as e:
        app.logger.error(e)
        return str(e)


@app.route("/rocket", methods=["GET"])
def shadowrocket():
    try:
        log_data = {
            "method": request.method,
            "path": request.path,
            "args": request.args,
            "data": request.data.decode("utf-8")
        }

        with open("template/shadowrocket-template.conf", "r") as file:

            app.logger.info(log_data)
            shaowrocket_configuration = file.read()
            response = Response(shaowrocket_configuration, content_type="text/plain; charset=utf-8")

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

        config = configparser.ConfigParser()
        config.read("src/config.ini")
        sub_link = config["proxy_link"]["sub_link"]

        app.logger.info(log_data)

        sub_link_transfer = SubLinkTransfer(sub_link)
        proxies = sub_link_transfer.get_proxies_result()

        allow_directives = []

        for item in proxies:
            if "server" in item:
                ip_address = item["server"]
                allow_directive = f"allow {ip_address};"
                allow_directives.append(allow_directive)

        # Write the directives to a file
        with open("resource/allowed_ips.conf", "w") as file:
            for directive in allow_directives:
                file.write(directive + "\n")

            hide_allow_directives = [re.sub(r"\d+.", "*.", i, 2) for i in allow_directives]
            return f"Update allow list successfully. IP list: {hide_allow_directives}"

    except Exception as e:
        app.logger.error(e)
        return str(e)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
