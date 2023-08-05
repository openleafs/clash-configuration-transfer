import logging
import configparser

import yaml
from flask import Flask, request, Response

from sub_link_transfer import SubLinkTransfer

app = Flask(__name__)

logging.basicConfig(filename="clash_configuration_transfer.log", level=logging.DEBUG,
                    format=f"%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s")


@app.route("/transfer", methods=["GET"])
def transfer():
    try:
        log_data = {
            "request_method": request.method,
            "request_path": request.path,
            "request_args": request.args,
            "request_data": request.data.decode("utf-8")
        }

        pass_link = request.args.get("pass_link")

        if int(pass_link) == 0:
            config = configparser.ConfigParser()
            config.read("config.ini")
            sub_link = config["proxy_link"]["sub_link"]
            custom_link = config["proxy_link"]["custom_link"]
        else:
            sub_link = request.args.get("sub_link")
            custom_link = request.args.get("custom_link")

            if sub_link is None:
                raise ValueError("You must offer at least a sub link")

        app.logger.info(log_data)

        sub_link_transfer = SubLinkTransfer(sub_link, custom_link)
        self_clash_configuration = sub_link_transfer.get_result()

        yaml_data = yaml.dump(self_clash_configuration)
        response = Response(yaml_data, content_type="text/plain; charset=utf-8")

        return response
    except Exception as e:
        app.logger.error(e)
        return str(e)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
