import json

from torchapi.api import handle


def main():
    with open("example_base64.txt", "r") as f:
        image_base64 = f.read()
    request = {"request": "banknote", "image": image_base64}
    request_json = json.dumps(request)
    response = handle(request_json)
    print(response["response"])


if __name__ == "__main__":
    main()

