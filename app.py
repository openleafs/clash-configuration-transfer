import yaml
from flask import Flask, request, Response

from sub_link_transfer import SubLinkTransfer

app = Flask(__name__)


# Route decorator to handle GET requests at the root URL "/"
@app.route("/transfer", methods=["GET"])
def transfer():
    sub_link = request.args.get("sub_link")
    custom_link = request.args.get("custom_link")
    sub_link_transfer = SubLinkTransfer(sub_link, custom_link)
    self_clash_configuration = sub_link_transfer.get_result()

    yaml_data = yaml.dump(self_clash_configuration)
    response = Response(yaml_data, content_type="text/yaml")
    response.headers["Content-Disposition"] = "attachment; filename=data.yaml"

    return self_clash_configuration


if __name__ == '__main__':
    app.run()
