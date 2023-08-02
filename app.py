import yaml
from flask import Flask, request, Response

from sub_link_transfer import SubLinkTransfer

app = Flask(__name__)


# Route decorator to handle GET requests at the root URL "/"
@app.route("/transfer", methods=["GET"])
def transfer():
    try:
        sub_link = request.args.get("sub_link")
        custom_link = request.args.get("custom_link")

        if sub_link is None or custom_link is None:
            return "please offer both sub link and custom link"

        sub_link_transfer = SubLinkTransfer(sub_link, custom_link)
        self_clash_configuration = sub_link_transfer.get_result()

        yaml_data = yaml.dump(self_clash_configuration)
        response = Response(yaml_data, content_type="text/plain; charset=utf-8")

        return response
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run(host="0.0.0.0")
